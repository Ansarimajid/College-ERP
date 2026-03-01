import json
import os
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse

from .EmailBackend import EmailBackend
from .models import Attendance, Session, Subject 

# Create your views here.


def login_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif request.user.user_type == '2':
            return redirect(reverse("staff_home"))
        else:
            return redirect(reverse("student_home"))
    return render(request, 'main_app/login.html')


def doLogin(request, **kwargs):
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")
    else:
        #Google recaptcha
        captcha_token = request.POST.get('g-recaptcha-response')
        captcha_url = "https://www.google.com/recaptcha/api/siteverify"
        captcha_key = os.environ.get('RECAPTCHA_SECRET_KEY', '')
        data = {
            'secret': captcha_key,
            'response': captcha_token
        }
        # Make request
        try:
            captcha_server = requests.post(url=captcha_url, data=data)
            response = json.loads(captcha_server.text)
            if response['success'] == False:
                messages.error(request, 'Invalid Captcha. Try Again')
                return redirect('/')
        except:
            messages.error(request, 'Captcha could not be verified. Try Again')
            return redirect('/')
        
        #Authenticate
        user = EmailBackend.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            
            # Handle "Remember Me" functionality
            remember_me = request.POST.get('remember')
            if remember_me:
                # Set session to expire when browser closes = False
                # Session will last for 30 days
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days in seconds
            else:
                # Set session to expire when browser closes
                request.session.set_expiry(0)
            
            if user.user_type == '1':
                return redirect(reverse("admin_home"))
            elif user.user_type == '2':
                return redirect(reverse("staff_home"))
            else:
                return redirect(reverse("student_home"))
        else:
            messages.error(request, "Invalid details")
            return redirect("/")



def logout_user(request):
    if request.user != None:
        logout(request)
    return redirect("/")


def get_attendance(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')

    if not subject_id or not session_id:
        return JsonResponse({'error': 'Both subject and session are required'}, status=400)

    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)

        if request.user.user_type == '2' and subject.staff.admin_id != request.user.id:
            return HttpResponseForbidden('You are not allowed to access this subject attendance')
        if request.user.user_type == '3':
            return HttpResponseForbidden('Students cannot fetch staff attendance data')

        attendance = Attendance.objects.filter(subject=subject, session=session)
        attendance_list = []
        for attd in attendance:
            data = {
                    "id": attd.id,
                    "attendance_date": str(attd.date),
                    "session": attd.session.id
                    }
            attendance_list.append(data)
        return JsonResponse(attendance_list, safe=False)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid request parameters'}, status=400)


def showFirebaseJS(request):
    data = """
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');
firebase.initializeApp({
    apiKey: "%s",
    authDomain: "%s",
    databaseURL: "%s",
    projectId: "%s",
    storageBucket: "%s",
    messagingSenderId: "%s",
    appId: "%s",
    measurementId: "%s"
});
const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
    const notification = JSON.parse(payload);
    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    }
    return self.registration.showNotification(payload.notification.title, notificationOption);
});
    """ % (
        os.environ.get('FIREBASE_API_KEY', ''),
        os.environ.get('FIREBASE_AUTH_DOMAIN', ''),
        os.environ.get('FIREBASE_DATABASE_URL', ''),
        os.environ.get('FIREBASE_PROJECT_ID', ''),
        os.environ.get('FIREBASE_STORAGE_BUCKET', ''),
        os.environ.get('FIREBASE_MESSAGING_SENDER_ID', ''),
        os.environ.get('FIREBASE_APP_ID', ''),
        os.environ.get('FIREBASE_MEASUREMENT_ID', ''),
    )
    return HttpResponse(data, content_type='application/javascript')
