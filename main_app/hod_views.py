import json
import os
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from .decorators import admin_only
from .forms import *
from .models import *


@admin_only
def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    total_course = Course.objects.all().count()
    total_groups = Group.objects.filter(is_archived=False).count()

    # Attendance chart: per active group
    active_groups = Group.objects.filter(is_archived=False).select_related('course')
    group_label_list = [g.name[:12] for g in active_groups]
    group_attendance_list = [
        Attendance.objects.filter(group=g).count() for g in active_groups
    ]

    # Students per program
    course_all = Course.objects.all()
    course_name_list = []
    student_count_list_in_course = []
    for course in course_all:
        course_name_list.append(course.name)
        student_count_list_in_course.append(Student.objects.filter(course_id=course.id).count())

    # Student attendance overview
    student_attendance_present_list = []
    student_attendance_leave_list = []
    student_name_list = []
    for student in Student.objects.select_related('admin').all():
        present = AttendanceReport.objects.filter(
            student_id=student.id, status__in=[AttendanceReport.PRESENT, AttendanceReport.LATE]
        ).count()
        absent = AttendanceReport.objects.filter(
            student_id=student.id, status=AttendanceReport.ABSENT
        ).count()
        leave = LeaveReportStudent.objects.filter(student_id=student.id, status=1).count()
        student_attendance_present_list.append(present)
        student_attendance_leave_list.append(leave + absent)
        student_name_list.append(student.admin.first_name)

    context = {
        'page_title': "Administrative Dashboard",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_course': total_course,
        'total_groups': total_groups,
        'group_label_list': group_label_list,
        'group_attendance_list': group_attendance_list,
        'student_attendance_present_list': student_attendance_present_list,
        'student_attendance_leave_list': student_attendance_leave_list,
        'student_name_list': student_name_list,
        'student_count_list_in_course': student_count_list_in_course,
        'course_name_list': course_name_list,
    }
    return render(request, 'hod_template/home_content.html', context)


@admin_only
def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Teacher'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic')
            try:
                passport_url = ''
                if passport:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.save()
                staff_obj = Staff.objects.get(admin=user)
                staff_obj.course = course
                staff_obj.is_active = form.cleaned_data.get('is_active', True)
                staff_obj.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")

    return render(request, 'hod_template/add_staff_template.html', context)


@admin_only
def add_student(request):
    student_form = AddStudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Add Student'}
    if request.method == 'POST':
        if student_form.is_valid():
            first_name  = student_form.cleaned_data.get('first_name')
            last_name   = student_form.cleaned_data.get('last_name')
            address     = student_form.cleaned_data.get('address')
            email       = student_form.cleaned_data.get('email')
            gender      = student_form.cleaned_data.get('gender')
            password    = student_form.cleaned_data.get('password')
            course      = student_form.cleaned_data.get('course')
            group       = student_form.cleaned_data.get('group')
            passport    = request.FILES.get('profile_pic')
            try:
                passport_url = ''
                if passport:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3,
                    first_name=first_name, last_name=last_name,
                    profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.save()
                student = user.student
                student.course = course
                student.session = None
                student.save()
                if group:
                    Enrollment.objects.get_or_create(student=student, group=group, defaults={'is_active': True})
                    NotificationStudent.objects.create(
                        student=student,
                        message=f"Welcome! You have been enrolled in {group.name}.",
                    )
                    messages.success(request, f"Student added and enrolled in '{group.name}'.")
                else:
                    messages.success(request, f"Student {first_name} {last_name} added. Enroll them in a group from the Enrollments page.")
                return redirect(reverse('add_student'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Please fix the errors below.")
    return render(request, 'hod_template/add_student_template.html', context)


@admin_only
def add_course(request):
    form = CourseForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course()
                course.name = name
                course.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_course'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_course_template.html', context)


@admin_only
def add_subject(request):
    form = SubjectForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject()
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_subject'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_subject_template.html', context)


@admin_only
def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': 'Manage Teachers'
    }
    return render(request, "hod_template/manage_staff.html", context)


@admin_only
def manage_student(request):
    students = CustomUser.objects.filter(user_type=3)
    context = {
        'students': students,
        'page_title': 'Manage Students'
    }
    return render(request, "hod_template/manage_student.html", context)


@admin_only
def manage_course(request):
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Manage Courses'
    }
    return render(request, "hod_template/manage_course.html", context)


@admin_only
def manage_subject(request):
    subjects = Subject.objects.all()
    context = {
        'subjects': subjects,
        'page_title': 'Manage Subjects'
    }
    return render(request, "hod_template/manage_subject.html", context)


@admin_only
def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    form = StaffEditForm(request.POST or None, request.FILES or None, instance=staff)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Edit Teacher'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            is_active = form.cleaned_data.get('is_active', True)
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=staff.admin.id)
                user.email = email
                if password is not None:
                    user.set_password(password)
                if passport is not None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                staff.course = course
                staff.is_active = is_active
                user.save()
                staff.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fill form properly")
    return render(request, "hod_template/edit_staff_template.html", context)


@admin_only
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        'form': form,
        'student_id': student_id,
        'page_title': 'Edit Student'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                if passport is not None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.email = email
                if password is not None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                student.course = course
                user.save()
                student.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_student', args=[student_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    return render(request, "hod_template/edit_student_template.html", context)


@admin_only
def edit_course(request, course_id):
    instance = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Edit Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course.objects.get(id=course_id)
                course.name = name
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)


@admin_only
def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Edit Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject.objects.get(id=subject_id)
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'hod_template/edit_subject_template.html', context)


@admin_only
def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Created")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_session_template.html", context)


@admin_only
def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Manage Sessions'}
    return render(request, "hod_template/manage_session.html", context)


@admin_only
def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Edit Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Session Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


@csrf_exempt
@admin_only
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
@admin_only
def student_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStudent.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Student Feedback Messages'
        }
        return render(request, 'hod_template/student_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStudent, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
@admin_only
def staff_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Teacher Feedback'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
@admin_only
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Teacher Leave Requests'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
@admin_only
def view_student_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Students'
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@admin_only
def admin_view_attendance(request):
    groups = Group.objects.filter(is_archived=False).select_related('course', 'teacher__admin')
    context = {
        'groups': groups,
        'page_title': 'View Attendance',
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
@admin_only
def get_admin_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    group_id = request.POST.get('group')
    try:
        if attendance_date_id:
            attendance = get_object_or_404(Attendance, id=attendance_date_id)
            reports = AttendanceReport.objects.filter(attendance=attendance).select_related('student')
            data = [{"status": r.status, "name": str(r.student)} for r in reports]
            return JsonResponse(json.dumps(data), safe=False)
        # Return list of attendance dates for a group
        group = get_object_or_404(Group, id=group_id)
        dates = Attendance.objects.filter(group=group).order_by('-date')
        data = [{"id": a.id, "attendance_date": str(a.date)} for a in dates]
        return JsonResponse(json.dumps(data), safe=False)
    except Exception:
        return JsonResponse({'error': 'Unable to fetch attendance.'}, status=400)


@admin_only
def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                email = form.cleaned_data.get('email')
                gender = form.cleaned_data.get('gender')
                address = form.cleaned_data.get('address')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                if email:
                    custom_user.email = email
                if gender:
                    custom_user.gender = gender
                if address is not None:
                    custom_user.address = address
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


@admin_only
def admin_notify_staff(request):
    staff = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Notify Teachers",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


@admin_only
def admin_notify_student(request):
    student = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Notify Students",
        'students': student
    }
    return render(request, "hod_template/student_notification.html", context)


@csrf_exempt
@admin_only
def send_student_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Student, admin_id=id)
    try:
        fcm_server_key = os.environ.get('FCM_SERVER_KEY', '')
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('student_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': student.admin.fcm_token
        }
        headers = {
            'Authorization': 'key=' + fcm_server_key,
            'Content-Type': 'application/json',
        }
        requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStudent(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
@admin_only
def send_staff_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        fcm_server_key = os.environ.get('FCM_SERVER_KEY', '')
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('staff_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': staff.admin.fcm_token
        }
        headers = {
            'Authorization': 'key=' + fcm_server_key,
            'Content-Type': 'application/json',
        }
        requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(staff=staff, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@admin_only
def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff deleted successfully!")
    except IntegrityError:
        messages.error(
            request,
            "Could not delete staff because related attendance data exists."
        )
    return redirect(reverse('manage_staff'))


@admin_only
def delete_student(request, student_id):
    student_user = get_object_or_404(CustomUser, student__id=student_id)
    try:
        with transaction.atomic():
            student_profile = student_user.student
            # AttendanceReport keeps a DO_NOTHING FK to Student, so remove it manually.
            AttendanceReport.objects.filter(student=student_profile).delete()
            student_user.delete()
        messages.success(request, "Student deleted successfully!")
    except IntegrityError:
        messages.error(
            request,
            "Could not delete student because related records still exist."
        )
    return redirect(reverse('manage_student'))


@admin_only
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some students are assigned to this course already. Kindly change the affected student course and try again")
    return redirect(reverse('manage_course'))


@admin_only
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject deleted successfully!")
    except IntegrityError:
        messages.error(
            request,
            "Could not delete subject because attendance records are linked to it."
        )
    return redirect(reverse('manage_subject'))


@admin_only
def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Session deleted successfully!")
    except Exception:
        messages.error(
            request, "There are students assigned to this session. Please move them to another session.")
    return redirect(reverse('manage_session'))


@csrf_exempt
@admin_only
def get_teachers_for_course(request):
    course_id = request.GET.get('course_id') or request.POST.get('course_id')
    try:
        teachers = Staff.objects.filter(
            course_id=course_id, is_active=True
        ).select_related('admin').order_by('admin__last_name')
        data = [{'id': t.id, 'name': f"{t.admin.first_name} {t.admin.last_name}"} for t in teachers]
        return JsonResponse(data, safe=False)
    except Exception:
        return JsonResponse([], safe=False)


@csrf_exempt
@admin_only
def get_groups_for_teacher(request):
    teacher_id = request.GET.get('teacher_id') or request.POST.get('teacher_id')
    course_id = request.GET.get('course_id') or request.POST.get('course_id')
    try:
        qs = Group.objects.filter(is_archived=False).select_related('course', 'teacher__admin')
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        elif course_id:
            qs = qs.filter(course_id=course_id)
        qs = qs.order_by('name')
        data = [
            {
                'id': g.id,
                'name': (
                    g.name
                    + (f" · {g.course.name}" if g.course else "")
                    + (f" · {g.teacher}" if g.teacher else "")
                )
            }
            for g in qs
        ]
        return JsonResponse(data, safe=False)
    except Exception:
        return JsonResponse([], safe=False)


# ── Branch CRUD ──────────────────────────────────────────────────────────────

@admin_only
def manage_branch(request):
    branches = Branch.objects.all()
    return render(request, 'hod_template/manage_branch.html', {
        'branches': branches,
        'page_title': 'Manage Branches',
    })


@admin_only
def add_branch(request):
    form = BranchForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Branch added successfully!")
            return redirect(reverse('manage_branch'))
    return render(request, 'hod_template/add_branch.html', {
        'form': form,
        'page_title': 'Add Branch',
    })


@admin_only
def edit_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    form = BranchForm(request.POST or None, instance=branch)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Branch updated!")
            return redirect(reverse('manage_branch'))
    return render(request, 'hod_template/add_branch.html', {
        'form': form,
        'page_title': 'Edit Branch',
    })


@admin_only
def delete_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    try:
        branch.delete()
        messages.success(request, "Branch deleted!")
    except Exception:
        messages.error(request, "Could not delete branch — it has groups linked to it.")
    return redirect(reverse('manage_branch'))


# ── Group CRUD ───────────────────────────────────────────────────────────────

@admin_only
def manage_group(request):
    groups = Group.objects.select_related('course', 'teacher', 'branch').all()
    return render(request, 'hod_template/manage_group.html', {
        'groups': groups,
        'page_title': 'Manage Groups',
    })


@admin_only
def add_group(request):
    form = GroupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Group created!")
            return redirect(reverse('manage_group'))
    return render(request, 'hod_template/add_group.html', {
        'form': form,
        'page_title': 'Add Group',
    })


@admin_only
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    form = GroupForm(request.POST or None, instance=group)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Group updated!")
            return redirect(reverse('manage_group'))
    return render(request, 'hod_template/add_group.html', {
        'form': form,
        'page_title': 'Edit Group',
    })


@admin_only
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    student_count = Enrollment.objects.filter(group=group).count()
    attendance_count = Attendance.objects.filter(group=group).count()
    result_count = StudentResult.objects.filter(group=group).count()

    if student_count or attendance_count or result_count:
        parts = []
        if student_count:
            parts.append(f"{student_count} enrollment(s)")
        if attendance_count:
            parts.append(f"{attendance_count} attendance record(s)")
        if result_count:
            parts.append(f"{result_count} result(s)")
        messages.warning(
            request,
            f"Cannot delete \"{group.name}\" — it has {', '.join(parts)}. "
            f"Archive it instead to hide it without losing data."
        )
        return redirect(reverse('manage_group'))

    try:
        group.delete()
        messages.success(request, f"Group \"{group.name}\" deleted.")
    except Exception as e:
        messages.error(request, f"Could not delete group: {e}")
    return redirect(reverse('manage_group'))


@admin_only
def archive_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.is_archived = not group.is_archived
    group.save()
    action = "archived" if group.is_archived else "restored"
    messages.success(request, f"Group \"{group.name}\" {action}.")
    return redirect(reverse('manage_group'))


# ── Enrollment management ────────────────────────────────────────────────────

@admin_only
def manage_enrollment(request):
    group_id = request.GET.get('group')
    groups = Group.objects.filter(is_archived=False).select_related('course')
    enrollments = Enrollment.objects.select_related(
        'student__admin', 'student__course',
        'group__course', 'group__teacher__admin'
    ).all().order_by('group__name', 'student__admin__last_name')
    if group_id:
        enrollments = enrollments.filter(group_id=group_id)
    return render(request, 'hod_template/manage_enrollment.html', {
        'enrollments': enrollments,
        'groups': groups,
        'selected_group': group_id,
        'page_title': 'Enrollments',
    })


@admin_only
def add_enrollment(request):
    groups = Group.objects.filter(is_archived=False).select_related('course', 'teacher__admin')
    students = Student.objects.select_related('admin', 'course').order_by('admin__last_name')

    if request.method == 'POST':
        group_id = request.POST.get('group')
        student_id = request.POST.get('student')
        is_active = request.POST.get('is_active', 'True') == 'True'
        errors = {}
        if not group_id:
            errors['group'] = 'Please select a group.'
        if not student_id:
            errors['student'] = 'Please select a student.'
        if not errors:
            try:
                group = get_object_or_404(Group, id=group_id)
                student = get_object_or_404(Student, id=student_id)
                _, created = Enrollment.objects.get_or_create(
                    student=student, group=group,
                    defaults={'is_active': is_active}
                )
                if created:
                    NotificationStudent.objects.create(
                        student=student,
                        message=f"You have been enrolled in {group.name}" + (f" ({group.course.name})" if group.course else "") + ".",
                    )
                    messages.success(request, f"{student} enrolled in {group.name}.")
                    return redirect(reverse('manage_enrollment'))
                else:
                    errors['student'] = f"{student} is already enrolled in {group.name}."
            except (ValueError, TypeError):
                errors['error'] = 'Invalid selection. Please choose valid group and student.'
            except Exception as e:
                errors['error'] = f"Could not enroll: {e}"

        return render(request, 'hod_template/add_enrollment.html', {
            'groups': groups,
            'students': students,
            'errors': errors,
            'posted': request.POST,
            'page_title': 'Enroll Student',
        })

    return render(request, 'hod_template/add_enrollment.html', {
        'groups': groups,
        'students': students,
        'page_title': 'Enroll Student',
    })


@csrf_exempt
@admin_only
def get_group_info(request):
    group_id = request.POST.get('group_id')
    group = get_object_or_404(Group, id=group_id)
    enrolled_ids = list(Enrollment.objects.filter(group=group).values_list('student_id', flat=True))
    data = {
        'teacher': str(group.teacher) if group.teacher else '—',
        'program': group.course.name if group.course else '—',
        'schedule': group.schedule or '—',
        'enrolled_count': len(enrolled_ids),
        'capacity': group.capacity,
        'enrolled_ids': enrolled_ids,
    }
    return JsonResponse(data)


@admin_only
def delete_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    enrollment.delete()
    messages.success(request, "Enrollment removed.")
    return redirect(reverse('manage_enrollment'))
