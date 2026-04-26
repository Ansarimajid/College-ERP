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
    total_students = Student.objects.filter(course=staff.course).count()
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()
    subjects = Subject.objects.filter(staff=staff)
    total_subject = subjects.count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name)
        attendance_list.append(attendance_count)
    context = {
        'page_title': str(staff.admin.first_name) + ' ' + str(staff.admin.last_name) + ' · ' + str(staff.course),
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list
    }
    return render(request, "staff_template/erpnext_staff_home.html", context)


def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    groups = Group.objects.filter(teacher=staff).select_related('course', 'branch')
    context = {
        'groups': groups,
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


@csrf_exempt
def save_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    group_id = request.POST.get('group')
    students = json.loads(student_data)
    try:
        group = get_object_or_404(Group, id=group_id)
        attendance = Attendance(group=group, date=date)
        attendance.save()
        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get('id'))
            AttendanceReport(
                student=student,
                attendance=attendance,
                status=student_dict.get('status'),
            ).save()
    except Exception:
        return HttpResponse("ERROR", status=400)
    return HttpResponse("OK")


def staff_update_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    groups = Group.objects.filter(teacher=staff).select_related('course', 'branch')
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
        reports = AttendanceReport.objects.filter(attendance=attendance).select_related('student__admin')
        student_data = [
            {
                "id": r.student.admin.id,
                "name": r.student.admin.last_name + " " + r.student.admin.first_name,
                "status": r.status,
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
            student = get_object_or_404(Student, admin_id=student_dict.get('id'))
            report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
            report.status = student_dict.get('status')
            report.save()
    except Exception:
        return HttpResponse("ERROR", status=400)
    return HttpResponse("OK")


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


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    groups = Group.objects.filter(teacher=staff).select_related('course')
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
        else:
            messages.error(request, "Form has errors!")
    # restrict subjects/groups to this teacher
    form.fields['subject'].queryset = Subject.objects.filter(staff=staff)
    form.fields['group'].queryset = Group.objects.filter(teacher=staff)
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
        else:
            messages.error(request, "Form has errors!")
    form.fields['subject'].queryset = Subject.objects.filter(staff=staff)
    form.fields['group'].queryset = Group.objects.filter(teacher=staff)
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
