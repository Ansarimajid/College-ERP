import json
import logging
import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView
from django.db import DatabaseError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from .EmailBackend import EmailBackend
from .apps import create_recovery_admin_access
from .models import Admin, Attendance, Session, Staff, Student, Subject

logger = logging.getLogger(__name__)


def _ensure_role_profile(user):
    """Best-effort role profile healing to avoid login-time crashes."""
    user_type = str(user.user_type)
    model_map = {
        '1': Admin,
        '2': Staff,
        '3': Student,
    }
    profile_model = model_map.get(user_type)
    if profile_model is None:
        return

    try:
        if not profile_model.objects.filter(admin=user).exists():
            profile_model.objects.create(admin=user)
    except Exception:
        # Keep login flow alive; dashboard views will enforce access rules.
        logger.exception("Role profile healing failed for user pk=%s", user.pk)


def _redirect_authenticated_user(user):
    """Return the correct home redirect for an already-logged-in user."""
    user_type = str(user.user_type)
    if user_type == '1':
        return redirect(reverse("admin_home"))
    if user_type == '2':
        return redirect(reverse("staff_home"))
    if user_type == '3':
        return redirect(reverse("student_home"))
    return None  # Unknown type — fall through to show login page


def login_page(request):
    if request.user.is_authenticated:
        destination = _redirect_authenticated_user(request.user)
        if destination:
            return destination
    return render(request, 'main_app/login.html')


def doLogin(request, **kwargs):
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")

    # Normalise email: strip whitespace and lowercase for consistent lookup.
    email = (request.POST.get('email') or '').strip().lower()
    password = request.POST.get('password') or ''

    if not email or not password:
        messages.error(request, "Please enter both email and password.")
        return redirect("/")

    user = authenticate(request, username=email, password=password)

    # Recovery fallback: only fires for the designated recovery account.
    recovery_email = os.environ.get(
        'RECOVERY_ADMIN_EMAIL', 'iceberg.edu.center@gmail.com'
    ).strip().lower()

    if user is None and email == recovery_email:
        try:
            create_recovery_admin_access(sender=None, force_password=True)
            user = authenticate(request, username=email, password=password)
        except Exception as exc:
            logger.error("Recovery admin re-seed failed: %s", exc)
            user = None

    if user is None:
        messages.error(request, "Invalid email or password.")
        return redirect("/")

    try:
        login(request, user)
    except DatabaseError:
        logger.exception("Login failed due to session/database error for email=%s", email)
        messages.error(
            request,
            "Login is temporarily unavailable. Please try again in a moment."
        )
        return redirect("/")
    except Exception:
        logger.exception("Unexpected login failure for email=%s", email)
        messages.error(
            request,
            "Login failed due to a server issue. Please try again shortly."
        )
        return redirect("/")

    # Ensure the role profile row exists (heals accounts created before signals).
    user_type = str(user.user_type)
    _ensure_role_profile(user)

    # Remember Me
    if request.POST.get('remember'):
        request.session.set_expiry(30 * 24 * 60 * 60)
    else:
        request.session.set_expiry(0)

    # Deterministic redirect — no catch-all else that silently misroutes users.
    if user_type == '1':
        return redirect(reverse("admin_home"))
    if user_type == '2':
        return redirect(reverse("staff_home"))
    if user_type == '3':
        return redirect(reverse("student_home"))

    # Unknown user_type: log it, inform the user, and log them out safely.
    logger.error(
        "Login rejected: user pk=%s has unrecognised user_type=%r",
        user.pk, user.user_type,
    )
    logout(request)
    messages.error(
        request,
        "Your account role is not configured correctly. "
        "Please contact the administrator."
    )
    return redirect("/")


def logout_user(request):
    if request.method != 'POST':
        # Ignore accidental GET hits on the logout URL — redirect to home.
        if request.user.is_authenticated:
            return _redirect_authenticated_user(request.user) or redirect("/")
        return redirect("/")

    if request.user is not None:
        logout(request)
    return redirect("/")


# ---------------------------------------------------------------------------
# Password reset — wraps Django's built-in view to prevent SMTP errors from
# becoming HTTP 500s.  Any exception during email dispatch is logged and the
# user is still sent to the "check your inbox" page (avoids email enumeration).
# ---------------------------------------------------------------------------

class SafePasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as exc:
            logger.error(
                "Password reset email dispatch failed: %s", exc, exc_info=True
            )
            # Still redirect to "done" — do not leak whether the address exists
            # and do not expose a 500 to the user.
            return HttpResponseRedirect(self.success_url)


# ---------------------------------------------------------------------------
# Shared AJAX / utility views
# ---------------------------------------------------------------------------

@csrf_exempt
def get_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = Attendance.objects.filter(subject=subject, session=session)
        attendance_list = []
        for attd in attendance:
            data = {
                "id": attd.id,
                "attendance_date": str(attd.date),
                "session": attd.session.id
            }
            attendance_list.append(data)
        return JsonResponse(json.dumps(attendance_list), safe=False)
    except Exception:
        return JsonResponse({'error': 'Unable to fetch attendance.'}, status=400)


def health(request):
    """Lightweight health-check endpoint for DO load-balancer probes."""
    from django.db import connection
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False
    status = 200 if db_ok else 503
    return JsonResponse({'status': 'ok' if db_ok else 'db_unavailable', 'db': db_ok}, status=status)


def showFirebaseJS(request):
    data = """
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

firebase.initializeApp({
    apiKey: "AIzaSyBarDWWHTfTMSrtc5Lj3Cdw5dEvjAkFwtM",
    authDomain: "sms-with-django.firebaseapp.com",
    databaseURL: "https://sms-with-django.firebaseio.com",
    projectId: "sms-with-django",
    storageBucket: "sms-with-django.appspot.com",
    messagingSenderId: "945324593139",
    appId: "1:945324593139:web:03fa99a8854bbd38420c86",
    measurementId: "G-2F2RXTL9GT"
});

const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
    const notification = JSON.parse(payload);
    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    };
    return self.registration.showNotification(
        payload.notification.title, notificationOption
    );
});
    """
    return HttpResponse(data, content_type='application/javascript')
