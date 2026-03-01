from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user  # Who is the current user ?

        # Allow shared views (login, logout, attendance, firebase) and django internals
        if modulename in ('main_app.views', 'django.contrib.auth.views',
                          'django.contrib.admin.sites', 'django.views.static'):
            return None

        if user.is_authenticated:
            if user.user_type == '1':  # Is it the HOD/Admin
                if modulename in ('main_app.student_views', 'main_app.staff_views'):
                    return redirect(reverse('admin_home'))
            elif user.user_type == '2':  # Staff
                if modulename in ('main_app.student_views', 'main_app.hod_views'):
                    return redirect(reverse('staff_home'))
            elif user.user_type == '3':  # Student
                if modulename in ('main_app.hod_views', 'main_app.staff_views'):
                    return redirect(reverse('student_home'))
            else:  # None of the aforementioned
                return redirect(reverse('login_page'))
        else:
            if request.path == reverse('login_page') or request.path == reverse('user_login'):
                pass
            else:
                return redirect(reverse('login_page'))
