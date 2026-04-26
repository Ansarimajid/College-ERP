import json
import math
from datetime import datetime

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .decorators import student_only
from .forms import *
from .models import *


@student_only
def student_home(request):
    student = get_object_or_404(Student, admin=request.user)
    total_subject = Subject.objects.filter(course=student.course).count()
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    total_present = AttendanceReport.objects.filter(student=student, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    subject_name = []
    data_present = []
    data_absent = []
    subject_rows = []  # list of dicts for the breakdown table
    subjects = Subject.objects.filter(course=student.course)
    for subject in subjects:
        attendance = Attendance.objects.filter(subject=subject)
        present_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=True, student=student).count()
        absent_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=False, student=student).count()
        total_cls = present_count + absent_count
        pct = round((present_count / total_cls) * 100) if total_cls > 0 else 0
        subject_name.append(subject.name)
        data_present.append(present_count)
        data_absent.append(absent_count)
        subject_rows.append({
            'name': subject.name,
            'present': present_count,
            'absent': absent_count,
            'total': total_cls,
            'pct': pct,
        })
    context = {
        'total_attendance': total_attendance,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'total_subject': total_subject,
        'subjects': subjects,
        'subject_rows': subject_rows,
        'data_present': data_present,
        'data_absent': data_absent,
        'data_name': subject_name,
        'page_title': 'Student Homepage'
    }
    return render(request, 'student_template/erpnext_student_home.html', context)


@ csrf_exempt
def student_view_attendance(request):
    student = get_object_or_404(Student, admin=request.user)
    enrolled_group_ids = Enrollment.objects.filter(
        student=student, is_active=True
    ).values_list('group_id', flat=True)
    groups = Group.objects.filter(id__in=enrolled_group_ids).select_related('course')

    if request.method != 'POST':
        context = {
            'groups': groups,
            'page_title': 'View Attendance',
        }
        return render(request, 'student_template/student_view_attendance.html', context)

    # AJAX POST: return attendance records for a group in a date range
    group_id = request.POST.get('group')
    start = request.POST.get('start_date')
    end = request.POST.get('end_date')
    try:
        group = get_object_or_404(Group, id=group_id)
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        attendance_qs = Attendance.objects.filter(
            group=group, date__range=(start_date, end_date)
        )
        reports = AttendanceReport.objects.filter(
            attendance__in=attendance_qs, student=student
        ).select_related('attendance')
        json_data = [
            {"date": str(r.attendance.date), "status": r.status}
            for r in reports.order_by('attendance__date')
        ]
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception:
        return JsonResponse({'error': 'Unable to fetch attendance.'}, status=400)


def student_apply_leave(request):
    form = LeaveReportStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStudent.objects.filter(student=student),
        'page_title': 'Apply for leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('student_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_apply_leave.html", context)


def student_feedback(request):
    form = FeedbackStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStudent.objects.filter(student=student),
        'page_title': 'Student Feedback'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Feedback submitted for review")
                return redirect(reverse('student_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_feedback.html", context)


def student_view_profile(request):
    student = get_object_or_404(Student, admin=request.user)
    form = StudentEditForm(request.POST or None, request.FILES or None,
                           instance=student)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = student.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                student.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('student_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "student_template/student_view_profile.html", context)


@csrf_exempt
def student_fcmtoken(request):
    token = request.POST.get('token')
    student_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        student_user.fcm_token = token
        student_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def student_view_notification(request):
    student = get_object_or_404(Student, admin=request.user)
    notifications = NotificationStudent.objects.filter(student=student)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "student_template/student_view_notification.html", context)


def student_view_result(request):
    student = get_object_or_404(Student, admin=request.user)
    results = StudentResult.objects.filter(student=student).select_related('group', 'subject')
    context = {
        'results': results,
        'page_title': "View Results",
    }
    return render(request, "student_template/student_view_result.html", context)


#library

def view_books(request):
    books = Book.objects.all()
    context = {
        'books': books,
        'page_title': "Library"
    }
    return render(request, "student_template/view_books.html", context)



# ── Assignments ───────────────────────────────────────────────────────────────

@student_only
def student_assignments(request):
    student = get_object_or_404(Student, admin=request.user)
    enrolled_groups = Enrollment.objects.filter(student=student, is_active=True).values_list('group_id', flat=True)
    assignments = Assignment.objects.filter(group__in=enrolled_groups).select_related('subject', 'group', 'created_by__admin').order_by('due_date')
    submitted_ids = set(Submission.objects.filter(student=student).values_list('assignment_id', flat=True))
    return render(request, 'student_template/student_assignments.html', {
        'assignments': assignments,
        'submitted_ids': submitted_ids,
        'page_title': 'Assignments',
    })


@student_only
def submit_assignment(request, assignment_id):
    student = get_object_or_404(Student, admin=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id)
    existing = Submission.objects.filter(assignment=assignment, student=student).first()
    form = SubmissionForm(request.POST or None, request.FILES or None, instance=existing)
    if request.method == 'POST':
        if form.is_valid():
            obj = form.save(commit=False)
            obj.assignment = assignment
            obj.student = student
            obj.save()
            messages.success(request, "Submitted successfully!")
            return redirect(reverse('student_assignments'))
        else:
            messages.error(request, "Form has errors!")
    return render(request, 'student_template/submit_assignment.html', {
        'form': form,
        'assignment': assignment,
        'existing': existing,
        'page_title': f'Submit — {assignment.title}',
    })
