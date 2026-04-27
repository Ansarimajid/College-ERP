import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .decorators import staff_only
from .forms import *
from .models import *
from . import forms, models
from datetime import date


@staff_only
def staff_home(request):
    staff = get_object_or_404(Staff, admin=request.user)
    groups = Group.objects.filter(teacher=staff, is_archived=False)
    total_groups = groups.count()
    total_students = (
        Enrollment.objects
        .filter(group__in=groups, is_active=True)
        .values('student').distinct().count()
    )
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()
    total_attendance = Attendance.objects.filter(group__in=groups).count()

    group_label_list = []
    attendance_list = []
    for group in groups:
        group_label_list.append(group.name[:12])
        attendance_list.append(Attendance.objects.filter(group=group).count())

    context = {
        'page_title': f"{staff.admin.first_name} {staff.admin.last_name}" + (f" · {staff.course}" if staff.course else ""),
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_subject': total_groups,
        'subject_list': group_label_list,
        'attendance_list': attendance_list,
    }
    return render(request, "staff_template/erpnext_staff_home.html", context)


@staff_only
def staff_take_attendance(request):
    # Show ALL non-archived groups so any teacher can take attendance
    groups = Group.objects.filter(is_archived=False).select_related('course', 'branch')
    context = {
        'groups': groups,
        'today': date.today().isoformat(),
        'page_title': 'Take Attendance',
    }
    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt
def get_students(request):
    group_id = request.POST.get('group')
    try:
        group = get_object_or_404(Group, id=group_id)
        enrollments = Enrollment.objects.filter(
            group=group, is_active=True
        ).select_related('student__admin')
        student_data = [
            {
                "id": e.student.id,
                "name": e.student.admin.last_name + " " + e.student.admin.first_name,
            }
            for e in enrollments
        ]
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception:
        return JsonResponse({'error': 'Unable to fetch students.'}, status=400)


_STATUS_LABELS = {
    AttendanceReport.ABSENT: 'Absent',
    AttendanceReport.PRESENT: 'Present',
    AttendanceReport.LATE: 'Late',
}


@csrf_exempt
def save_attendance(request):
    student_data = request.POST.get('student_ids')
    att_date = request.POST.get('date')
    group_id = request.POST.get('group')
    students = json.loads(student_data)
    try:
        group = get_object_or_404(Group, id=group_id)
        attendance = Attendance.objects.create(group=group, date=att_date)
        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict['id'])
            status = int(student_dict.get('status', AttendanceReport.ABSENT))
            AttendanceReport.objects.create(student=student, attendance=attendance, status=status)
            NotificationStudent.objects.create(
                student=student,
                message=(
                    f"Attendance for {group.name} on {att_date} has been marked: "
                    f"{_STATUS_LABELS.get(status, 'Unknown')}."
                ),
            )
    except Exception:
        return HttpResponse("ERROR", status=400)
    return HttpResponse("OK")


@staff_only
def staff_update_attendance(request):
    groups = Group.objects.filter(is_archived=False).select_related('course', 'branch')
    context = {
        'groups': groups,
        'page_title': 'Update Attendance',
    }
    return render(request, 'staff_template/staff_update_attendance.html', context)


@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        attendance = get_object_or_404(Attendance, id=attendance_date_id)
        reports = AttendanceReport.objects.filter(
            attendance=attendance
        ).select_related('student__admin')
        student_data = [
            {
                "id": r.student.id,   # student PK (not admin PK)
                "name": r.student.admin.last_name + " " + r.student.admin.first_name,
                "status": r.status,   # 0/1/2
            }
            for r in reports
        ]
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception:
        return JsonResponse({'error': 'Unable to fetch student attendance.'}, status=400)


@csrf_exempt
def update_attendance(request):
    student_data = request.POST.get('student_ids')
    attendance_id = request.POST.get('date')
    students = json.loads(student_data)
    try:
        attendance = get_object_or_404(Attendance, id=attendance_id)
        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict['id'])   # student PK
            report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
            status = int(student_dict.get('status', AttendanceReport.ABSENT))
            report.status = status
            report.save()
            NotificationStudent.objects.create(
                student=student,
                message=(
                    f"Attendance for {attendance.group.name} on {attendance.date} "
                    f"updated to {_STATUS_LABELS.get(status, 'Unknown')}."
                ),
            )
    except Exception:
        return HttpResponse("ERROR", status=400)
    return HttpResponse("OK")


@staff_only
def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff),
        'page_title': 'Apply for Leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "Could not apply!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_apply_leave.html", context)


@staff_only
def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Add Feedback'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_feedback.html", context)


@staff_only
def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None,instance=staff)
    context = {'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = staff.admin
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
                staff.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@staff_only
def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


@staff_only
def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    groups = Group.objects.filter(is_archived=False).select_related('course')
    context = {
        'page_title': 'Result Upload',
        'groups': groups,
    }
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_list')
            group_id = request.POST.get('group')
            test = request.POST.get('test')
            exam = request.POST.get('exam')
            student = get_object_or_404(Student, id=student_id)
            group = get_object_or_404(Group, id=group_id)
            result, created = StudentResult.objects.get_or_create(
                student=student, group=group,
                defaults={'test': test, 'exam': exam},
            )
            if not created:
                result.test = test
                result.exam = exam
                result.save()
            messages.success(request, "Scores " + ("Saved" if created else "Updated"))
        except Exception as e:
            messages.warning(request, "Error processing form: " + str(e))
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_student_result(request):
    try:
        group_id = request.POST.get('group')
        student_id = request.POST.get('student')
        student = get_object_or_404(Student, id=student_id)
        group = get_object_or_404(Group, id=group_id)
        result = StudentResult.objects.get(student=student, group=group)
        return HttpResponse(json.dumps({'exam': result.exam, 'test': result.test}))
    except StudentResult.DoesNotExist:
        return HttpResponse('False')
    except Exception:
        return HttpResponse('False')

#library
@staff_only
def add_book(request):
    if request.method == "POST":
        name = request.POST['name']
        author = request.POST['author']
        isbn = request.POST['isbn']
        category = request.POST['category']


        books = Book.objects.create(name=name, author=author, isbn=isbn, category=category )
        books.save()
        alert = True
        return render(request, "staff_template/add_book.html", {'alert':alert})
    context = {
        'page_title': "Add Book"
    }
    return render(request, "staff_template/add_book.html",context)

#issue book


@staff_only
def issue_book(request):
    form = forms.IssueBookForm()
    if request.method == "POST":
        form = forms.IssueBookForm(request.POST)
        if form.is_valid():
            obj = models.IssuedBook()
            obj.student_id = request.POST['name2']
            obj.isbn = request.POST['isbn2']
            obj.save()
            alert = True
            return render(request, "staff_template/issue_book.html", {'obj':obj, 'alert':alert})
    return render(request, "staff_template/issue_book.html", {'form':form})

@staff_only
def view_issued_book(request):
    issuedBooks = IssuedBook.objects.all()
    details = []
    for issued in issuedBooks:
        days = (date.today() - issued.issued_date).days
        fine = max(0, (days - 14) * 5)
        book = models.Book.objects.filter(isbn=issued.isbn).first()
        if book:
            details.append((book.name, book.isbn, issued.issued_date, issued.expiry_date, fine))
    return render(request, "staff_template/view_issued_book.html", {'issuedBooks': issuedBooks, 'details': details})

# ── Assignments ───────────────────────────────────────────────────────────────

@staff_only
def staff_assignments(request):
    staff = get_object_or_404(Staff, admin=request.user)
    assignments = Assignment.objects.filter(created_by=staff).select_related('subject', 'group').order_by('-created_at')
    return render(request, 'staff_template/staff_assignments.html', {
        'assignments': assignments,
        'page_title': 'Assignments',
    })


@staff_only
def add_assignment(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = AssignmentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = staff
            obj.save()
            messages.success(request, "Assignment created!")
            return redirect(reverse('staff_assignments'))
    form.fields['group'].queryset = Group.objects.filter(teacher=staff, is_archived=False)
    return render(request, 'staff_template/add_assignment.html', {
        'form': form,
        'page_title': 'Add Assignment',
    })


@staff_only
def edit_assignment(request, assignment_id):
    staff = get_object_or_404(Staff, admin=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id, created_by=staff)
    form = AssignmentForm(request.POST or None, instance=assignment)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated!")
            return redirect(reverse('staff_assignments'))
    form.fields['group'].queryset = Group.objects.filter(teacher=staff, is_archived=False)
    return render(request, 'staff_template/add_assignment.html', {
        'form': form,
        'page_title': 'Edit Assignment',
    })


@staff_only
def delete_assignment(request, assignment_id):
    staff = get_object_or_404(Staff, admin=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id, created_by=staff)
    assignment.delete()
    messages.success(request, "Assignment deleted.")
    return redirect(reverse('staff_assignments'))


@staff_only
def view_submissions(request, assignment_id):
    staff = get_object_or_404(Staff, admin=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id, created_by=staff)
    submissions = Submission.objects.filter(assignment=assignment).select_related('student__admin')
    return render(request, 'staff_template/view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
        'page_title': f'Submissions — {assignment.title}',
    })


@staff_only
def grade_submission(request, submission_id):
    staff = get_object_or_404(Staff, admin=request.user)
    submission = get_object_or_404(Submission, id=submission_id, assignment__created_by=staff)
    if request.method == 'POST':
        grade = request.POST.get('grade')
        try:
            submission.grade = float(grade)
            submission.save()
            messages.success(request, "Grade saved!")
        except (ValueError, TypeError):
            messages.error(request, "Invalid grade value.")
    return redirect(reverse('view_submissions', args=[submission.assignment_id]))


# ── Result Files ──────────────────────────────────────────────────────────────

_ALLOWED_RESULT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.webp'}


@staff_only
def staff_result_files(request):
    staff = get_object_or_404(Staff, admin=request.user)
    files = (
        ResultFile.objects
        .filter(uploaded_by=staff)
        .select_related('group', 'student__admin')
    )
    return render(request, 'staff_template/staff_result_files.html', {
        'files': files,
        'page_title': 'Result Files',
    })


@staff_only
def upload_result_file(request):
    import os
    staff = get_object_or_404(Staff, admin=request.user)
    groups = Group.objects.filter(is_archived=False).select_related('course')

    if request.method != 'POST':
        return render(request, 'staff_template/upload_result_file.html', {
            'groups': groups,
            'page_title': 'Upload Result File',
        })

    group_id = request.POST.get('group', '').strip()
    student_id = request.POST.get('student', '').strip() or None
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    uploaded_file = request.FILES.get('file')

    errors = {}
    if not group_id:
        errors['group'] = 'Please select a group.'
    if not title:
        errors['title'] = 'Title is required.'
    if not uploaded_file:
        errors['file'] = 'Please choose a file to upload.'
    elif os.path.splitext(uploaded_file.name)[1].lower() not in _ALLOWED_RESULT_EXTENSIONS:
        errors['file'] = 'Only PDF, Word (.doc/.docx), or image files are allowed.'

    if errors:
        return render(request, 'staff_template/upload_result_file.html', {
            'groups': groups,
            'errors': errors,
            'post': request.POST,
            'page_title': 'Upload Result File',
        })

    group = get_object_or_404(Group, id=group_id)
    student = get_object_or_404(Student, id=student_id) if student_id else None

    result_file = ResultFile.objects.create(
        group=group,
        student=student,
        file=uploaded_file,
        title=title,
        description=description,
        uploaded_by=staff,
    )

    if student:
        NotificationStudent.objects.create(
            student=student,
            message=f"A result file '{title}' has been uploaded for you in {group.name}.",
        )
    else:
        for e in Enrollment.objects.filter(group=group, is_active=True).select_related('student'):
            NotificationStudent.objects.create(
                student=e.student,
                message=f"A result file '{title}' has been uploaded for {group.name}.",
            )

    messages.success(request, f"File '{title}' uploaded successfully.")
    return redirect(reverse('staff_result_files'))


@staff_only
def delete_result_file(request, file_id):
    staff = get_object_or_404(Staff, admin=request.user)
    result_file = get_object_or_404(ResultFile, id=file_id, uploaded_by=staff)
    result_file.file.delete(save=False)
    result_file.delete()
    messages.success(request, "File deleted.")
    return redirect(reverse('staff_result_files'))
