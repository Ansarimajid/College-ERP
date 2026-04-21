from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user # Who is the current user ?
        user_type = str(getattr(user, 'user_type', ''))

        auth_allowed_paths = {
            reverse('login_page'),
            reverse('user_login'),
            reverse('user_logout'),
        }

        if user.is_authenticated:
            if user_type == '1': # Is it the HOD/Admin
                if modulename == 'main_app.student_views':
                    return redirect(reverse('admin_home'))
            elif user_type == '2': #  Staff :-/ ?
                if modulename == 'main_app.student_views' or modulename == 'main_app.hod_views':
                    return redirect(reverse('staff_home'))
            elif user_type == '3': # ... or Student ?
                if modulename == 'main_app.hod_views' or modulename == 'main_app.staff_views':
                    return redirect(reverse('student_home'))
            else:
                # Do not force logout for unknown/legacy user_type values.
                return None
        else:
            if (
                request.path in auth_allowed_paths
                or modulename.startswith('django.contrib.auth')
                or request.path.startswith('/admin/')
            ): # If the path is login or has anything to do with authentication, pass
                pass
            else:
                return redirect(reverse('login_page'))
