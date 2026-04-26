from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user
        user_type = str(getattr(user, 'user_type', ''))

        auth_allowed_paths = {
            reverse('login_page'),
            reverse('user_login'),
            reverse('user_logout'),
        }

        if user.is_authenticated:
            if user_type == '1':  # HOD / Admin
                if modulename in ('main_app.student_views', 'main_app.staff_views'):
                    return redirect(reverse('admin_home'))

            elif user_type == '2':  # Staff
                if modulename in ('main_app.student_views', 'main_app.hod_views'):
                    return redirect(reverse('staff_home'))

            elif user_type == '3':  # Student
                if modulename in ('main_app.hod_views', 'main_app.staff_views'):
                    return redirect(reverse('student_home'))

            else:
                # Unknown/corrupt user_type: log out and redirect to login.
                # This prevents a user with a broken account from reaching
                # any page while appearing authenticated.
                if request.path not in auth_allowed_paths:
                    logout(request)
                    return redirect(reverse('login_page'))

        else:
            if (
                request.path in auth_allowed_paths
                or modulename.startswith('django.contrib.auth')
                # /accounts/* covers both Django's built-in auth views AND our
                # SafePasswordResetView override (which lives in main_app.views
                # but is mounted under accounts/).
                or request.path.startswith('/accounts/')
                or request.path.startswith('/admin/')
                or request.path == '/health/'
            ):
                pass
            else:
                return redirect(reverse('login_page'))
