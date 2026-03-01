"""
Comprehensive test suite for College ERP application.
Tests models, views, middleware, utils, and forms.
"""
import json
from datetime import date, datetime, timedelta
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .forms import (
    CourseForm, FeedbackStaffForm, FeedbackStudentForm,
    IssueBookForm, LeaveReportStaffForm, LeaveReportStudentForm,
    SessionForm, StaffForm, StudentForm, SubjectForm,
)
from .models import (
    Admin, Attendance, AttendanceReport, Book, Course, CustomUser,
    FeedbackStaff, FeedbackStudent, IssuedBook, LeaveReportStaff,
    LeaveReportStudent, Library, NotificationStaff, NotificationStudent,
    Session, Staff, Student, StudentResult, Subject,
)
from .utils import handle_file_upload, validate_file_upload

CustomUserModel = get_user_model()


# ─── Helper: create a tiny valid image ────────────────────────────────
def _tiny_image(name="test.jpg"):
    """Return a minimal valid JPEG as SimpleUploadedFile."""
    # 1x1 white JPEG
    data = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01'
        b'\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07'
        b'\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14'
        b'\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f'
        b"'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
        b'\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08'
        b'\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03'
        b'\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12'
        b'!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1'
        b'\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTU'
        b'VWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93'
        b'\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9'
        b'\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6'
        b'\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2'
        b'\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7'
        b'\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd2\x8a'
        b'+\xff\xd9'
    )
    return SimpleUploadedFile(name, data, content_type="image/jpeg")


# ═══════════════════════════════════════════════════════════════════════
#  BASE TEST MIXIN — creates shared fixtures
# ═══════════════════════════════════════════════════════════════════════
class BaseTestMixin:
    """
    Mixin to create common users and objects for test cases.
    Call self._setup_data() in setUp().
    """

    def _setup_data(self):
        self.session = Session.objects.create(
            start_year=date(2025, 1, 1),
            end_year=date(2025, 12, 31),
        )
        self.course = Course.objects.create(name="Computer Science")
        # --- HOD / Admin ---
        self.hod_user = CustomUser.objects.create_user(
            email="hod@test.com", password="Pass1234!",
            user_type='1', first_name="Admin", last_name="User",
            gender="M", address="HOD Address",
        )
        self.admin_profile = Admin.objects.get(admin=self.hod_user)
        # --- Staff ---
        self.staff_user = CustomUser.objects.create_user(
            email="staff@test.com", password="Pass1234!",
            user_type='2', first_name="Staff", last_name="Member",
            gender="F", address="Staff Address",
        )
        self.staff_profile = Staff.objects.get(admin=self.staff_user)
        self.staff_profile.course = self.course
        self.staff_profile.save()
        # --- Student ---
        self.student_user = CustomUser.objects.create_user(
            email="student@test.com", password="Pass1234!",
            user_type='3', first_name="Student", last_name="Learner",
            gender="M", address="Student Address",
        )
        self.student_profile = Student.objects.get(admin=self.student_user)
        self.student_profile.course = self.course
        self.student_profile.session = self.session
        self.student_profile.save()
        # --- Subject ---
        self.subject = Subject.objects.create(
            name="Mathematics", staff=self.staff_profile, course=self.course
        )
        # --- Book ---
        self.book = Book.objects.create(
            name="Python 101", author="Guido", isbn=123456, category="Programming"
        )


# ═══════════════════════════════════════════════════════════════════════
#  1. MODEL TESTS
# ═══════════════════════════════════════════════════════════════════════
class ModelTests(BaseTestMixin, TestCase):
    def setUp(self):
        self._setup_data()

    # ── CustomUser & signals ──
    def test_user_str(self):
        self.assertEqual(str(self.hod_user), "Admin User")

    def test_admin_profile_created_by_signal(self):
        self.assertTrue(Admin.objects.filter(admin=self.hod_user).exists())

    def test_staff_profile_created_by_signal(self):
        self.assertTrue(Staff.objects.filter(admin=self.staff_user).exists())

    def test_student_profile_created_by_signal(self):
        self.assertTrue(Student.objects.filter(admin=self.student_user).exists())

    def test_create_superuser(self):
        su = CustomUser.objects.create_superuser(email="super@t.com", password="s")
        self.assertTrue(su.is_staff)
        self.assertTrue(su.is_superuser)

    # ── Session ──
    def test_session_str(self):
        self.assertIn("2025", str(self.session))

    # ── Course ──
    def test_course_str(self):
        self.assertEqual(str(self.course), "Computer Science")

    # ── Student FK SET_NULL ──
    def test_student_course_set_null_on_delete(self):
        self.course.delete()
        self.student_profile.refresh_from_db()
        self.assertIsNone(self.student_profile.course)

    # ── Book & IssuedBook ──
    def test_book_str(self):
        self.assertIn("123456", str(self.book))

    def test_issued_book_expiry_default(self):
        issued = IssuedBook.objects.create(
            student=self.student_profile, book=self.book
        )
        self.assertIsNotNone(issued.expiry_date)
        # expiry should be ~14 days from today
        self.assertAlmostEqual(
            (issued.expiry_date - date.today()).days, 14, delta=1
        )

    # ── Attendance cascade ──
    def test_attendance_cascade_on_subject_delete(self):
        att = Attendance.objects.create(
            session=self.session, subject=self.subject, date=date.today()
        )
        self.subject.delete()
        self.assertFalse(Attendance.objects.filter(id=att.id).exists())

    # ── AttendanceReport cascade ──
    def test_attendance_report_cascade(self):
        att = Attendance.objects.create(
            session=self.session, subject=self.subject, date=date.today()
        )
        report = AttendanceReport.objects.create(
            student=self.student_profile, attendance=att, status=True
        )
        att.delete()
        self.assertFalse(AttendanceReport.objects.filter(id=report.id).exists())

    # ── Leave date is DateField ──
    def test_leave_report_student_date_is_date(self):
        leave = LeaveReportStudent.objects.create(
            student=self.student_profile, date=date.today(), message="Sick"
        )
        self.assertIsInstance(leave.date, date)

    def test_leave_report_staff_date_is_date(self):
        leave = LeaveReportStaff.objects.create(
            staff=self.staff_profile, date=date.today(), message="Personal"
        )
        self.assertIsInstance(leave.date, date)

    # ── StudentResult ──
    def test_student_result_defaults(self):
        r = StudentResult.objects.create(
            student=self.student_profile, subject=self.subject
        )
        self.assertEqual(r.test, 0)
        self.assertEqual(r.exam, 0)

    # ── Library ──
    def test_library_str(self):
        lib = Library.objects.create(
            student=self.student_profile, book=self.book
        )
        self.assertIn("Learner", str(lib))

    # ── Feedback ──
    def test_feedback_student_creation(self):
        fb = FeedbackStudent.objects.create(
            student=self.student_profile, feedback="Great!", reply=""
        )
        self.assertEqual(fb.feedback, "Great!")

    def test_feedback_staff_creation(self):
        fb = FeedbackStaff.objects.create(
            staff=self.staff_profile, feedback="Improve labs", reply=""
        )
        self.assertEqual(fb.feedback, "Improve labs")

    # ── Notification ──
    def test_notification_student_creation(self):
        n = NotificationStudent.objects.create(
            student=self.student_profile, message="Hello"
        )
        self.assertEqual(n.message, "Hello")

    def test_notification_staff_creation(self):
        n = NotificationStaff.objects.create(
            staff=self.staff_profile, message="Meeting"
        )
        self.assertEqual(n.message, "Meeting")


# ═══════════════════════════════════════════════════════════════════════
#  2. UTILS TESTS  (file upload validation)
# ═══════════════════════════════════════════════════════════════════════
class UtilsTests(TestCase):

    def test_validate_none_returns_none(self):
        self.assertIsNone(validate_file_upload(None))

    def test_validate_allowed_extension(self):
        f = _tiny_image("photo.jpg")
        result = validate_file_upload(f)
        self.assertIsNotNone(result)

    def test_validate_disallowed_extension(self):
        f = SimpleUploadedFile("exploit.exe", b"\x00" * 100, content_type="application/octet-stream")
        with self.assertRaises(ValidationError):
            validate_file_upload(f)

    def test_validate_file_too_large(self):
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 5 * 1024 * 1024)
        f = SimpleUploadedFile("big.jpg", b"\x00" * (max_size + 1), content_type="image/jpeg")
        with self.assertRaises(ValidationError):
            validate_file_upload(f)

    def test_handle_file_upload_returns_url(self):
        f = _tiny_image("avatar.jpg")
        url = handle_file_upload(f)
        self.assertTrue(url.startswith("/"))
        # Filename should be a UUID (not original name)
        self.assertNotIn("avatar", url)


# ═══════════════════════════════════════════════════════════════════════
#  3. MIDDLEWARE TESTS
# ═══════════════════════════════════════════════════════════════════════
class MiddlewareTests(BaseTestMixin, TestCase):
    def setUp(self):
        self._setup_data()
        self.client = Client()

    # ── Unauthenticated redirects to login ──
    def test_unauthenticated_redirects_to_login(self):
        resp = self.client.get(reverse('admin_home'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/', resp.url)

    # ── Login page accessible unauthenticated ──
    def test_login_page_accessible(self):
        resp = self.client.get(reverse('login_page'))
        self.assertEqual(resp.status_code, 200)

    # ── HOD cannot access staff views ──
    def test_hod_blocked_from_staff_views(self):
        self.client.login(username="hod@test.com", password="Pass1234!")
        resp = self.client.get(reverse('staff_home'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('admin/home', resp.url)

    # ── HOD cannot access student views ──
    def test_hod_blocked_from_student_views(self):
        self.client.login(username="hod@test.com", password="Pass1234!")
        resp = self.client.get(reverse('student_home'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('admin/home', resp.url)

    # ── Staff cannot access HOD views ──
    def test_staff_blocked_from_hod_views(self):
        self.client.login(username="staff@test.com", password="Pass1234!")
        resp = self.client.get(reverse('admin_home'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('staff/home', resp.url)

    # ── Staff cannot access student views ──
    def test_staff_blocked_from_student_views(self):
        self.client.login(username="staff@test.com", password="Pass1234!")
        resp = self.client.get(reverse('student_home'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('staff/home', resp.url)

    # ── Student cannot access HOD views ──
    def test_student_blocked_from_hod_views(self):
        self.client.login(username="student@test.com", password="Pass1234!")
        resp = self.client.get(reverse('admin_home'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('student/home', resp.url)

    # ── Student cannot access staff views ──
    def test_student_blocked_from_staff_views(self):
        self.client.login(username="student@test.com", password="Pass1234!")
        resp = self.client.get(reverse('staff_home'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('student/home', resp.url)


# ═══════════════════════════════════════════════════════════════════════
#  4. SHARED VIEWS TESTS  (login, logout, get_attendance, firebase)
# ═══════════════════════════════════════════════════════════════════════
class SharedViewTests(BaseTestMixin, TestCase):
    def setUp(self):
        self._setup_data()
        self.client = Client()

    def test_login_page_renders(self):
        resp = self.client.get(reverse('login_page'))
        self.assertEqual(resp.status_code, 200)

    def test_login_page_redirects_authenticated_hod(self):
        self.client.login(username="hod@test.com", password="Pass1234!")
        resp = self.client.get(reverse('login_page'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('admin/home', resp.url)

    def test_doLogin_get_denied(self):
        resp = self.client.get(reverse('user_login'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Denied', resp.content)

    def test_logout(self):
        self.client.login(username="hod@test.com", password="Pass1234!")
        resp = self.client.get(reverse('user_logout'))
        self.assertEqual(resp.status_code, 302)

    def test_firebase_js(self):
        resp = self.client.get(reverse('showFirebaseJS'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/javascript')

    # ── get_attendance ──
    def test_get_attendance_rejects_get(self):
        self.client.login(username="staff@test.com", password="Pass1234!")
        resp = self.client.get(reverse('get_attendance'))
        self.assertEqual(resp.status_code, 405)

    def test_get_attendance_requires_auth(self):
        resp = self.client.post(reverse('get_attendance'), {
            'subject': self.subject.id, 'session': self.session.id
        })
        # Middleware redirects unauthenticated to login
        self.assertIn(resp.status_code, [302, 401])

    def test_get_attendance_missing_params(self):
        self.client.login(username="hod@test.com", password="Pass1234!")
        resp = self.client.post(reverse('get_attendance'), {})
        self.assertEqual(resp.status_code, 400)

    def test_get_attendance_success(self):
        self.client.login(username="hod@test.com", password="Pass1234!")
        Attendance.objects.create(
            session=self.session, subject=self.subject, date=date.today()
        )
        resp = self.client.post(reverse('get_attendance'), {
            'subject': self.subject.id, 'session': self.session.id
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data), 1)

    def test_get_attendance_student_forbidden(self):
        self.client.login(username="student@test.com", password="Pass1234!")
        resp = self.client.post(reverse('get_attendance'), {
            'subject': self.subject.id, 'session': self.session.id
        })
        self.assertEqual(resp.status_code, 403)


# ═══════════════════════════════════════════════════════════════════════
#  5. HOD VIEWS TESTS
# ═══════════════════════════════════════════════════════════════════════
class HodViewTests(BaseTestMixin, TestCase):
    def setUp(self):
        self._setup_data()
        self.client = Client()
        self.client.login(username="hod@test.com", password="Pass1234!")

    # ── Dashboard ──
    def test_admin_home(self):
        resp = self.client.get(reverse('admin_home'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('total_students', resp.context)

    # ── Manage pages ──
    def test_manage_staff_page(self):
        resp = self.client.get(reverse('manage_staff'))
        self.assertEqual(resp.status_code, 200)

    def test_manage_student_page(self):
        resp = self.client.get(reverse('manage_student'))
        self.assertEqual(resp.status_code, 200)

    def test_manage_course_page(self):
        resp = self.client.get(reverse('manage_course'))
        self.assertEqual(resp.status_code, 200)

    def test_manage_subject_page(self):
        resp = self.client.get(reverse('manage_subject'))
        self.assertEqual(resp.status_code, 200)

    def test_manage_session_page(self):
        resp = self.client.get(reverse('manage_session'))
        self.assertEqual(resp.status_code, 200)

    # ── Add course ──
    def test_add_course_get(self):
        resp = self.client.get(reverse('add_course'))
        self.assertEqual(resp.status_code, 200)

    def test_add_course_post(self):
        resp = self.client.post(reverse('add_course'), {'name': 'Biology'})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Course.objects.filter(name='Biology').exists())

    # ── Edit course ──
    def test_edit_course(self):
        resp = self.client.post(
            reverse('edit_course', args=[self.course.id]),
            {'name': 'CS Updated'}
        )
        self.assertEqual(resp.status_code, 200)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, 'CS Updated')

    # ── Delete course (POST required) ──
    def test_delete_course_get_rejected(self):
        resp = self.client.get(reverse('delete_course', args=[self.course.id]))
        self.assertEqual(resp.status_code, 405)

    def test_delete_course_post(self):
        c = Course.objects.create(name="Temp")
        resp = self.client.post(reverse('delete_course', args=[c.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Course.objects.filter(id=c.id).exists())

    # ── Add session ──
    def test_add_session(self):
        resp = self.client.post(reverse('add_session'), {
            'start_year': '2026-01-01', 'end_year': '2026-12-31'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Session.objects.filter(
            start_year=date(2026, 1, 1)).exists())

    # ── Edit session ──
    def test_edit_session(self):
        resp = self.client.post(
            reverse('edit_session', args=[self.session.id]),
            {'start_year': '2025-02-01', 'end_year': '2025-11-30'}
        )
        self.assertEqual(resp.status_code, 302)
        self.session.refresh_from_db()
        self.assertEqual(self.session.start_year, date(2025, 2, 1))

    # ── Delete session (POST required) ──
    def test_delete_session_get_rejected(self):
        resp = self.client.get(reverse('delete_session', args=[self.session.id]))
        self.assertEqual(resp.status_code, 405)

    def test_delete_session_post(self):
        s = Session.objects.create(
            start_year=date(2030, 1, 1), end_year=date(2030, 12, 31)
        )
        resp = self.client.post(reverse('delete_session', args=[s.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Session.objects.filter(id=s.id).exists())

    # ── Delete staff (POST required) ──
    def test_delete_staff_get_rejected(self):
        resp = self.client.get(
            reverse('delete_staff', args=[self.staff_profile.id])
        )
        self.assertEqual(resp.status_code, 405)

    def test_delete_staff_post(self):
        u = CustomUser.objects.create_user(
            email="del_staff@t.com", password="Pass1234!",
            user_type='2', first_name="Del", last_name="Staff",
            gender="M", address="x"
        )
        staff = Staff.objects.get(admin=u)
        resp = self.client.post(reverse('delete_staff', args=[staff.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(CustomUser.objects.filter(id=u.id).exists())

    # ── Delete student (POST required) ──
    def test_delete_student_post(self):
        u = CustomUser.objects.create_user(
            email="del_stu@t.com", password="Pass1234!",
            user_type='3', first_name="Del", last_name="Stu",
            gender="F", address="y"
        )
        stu = Student.objects.get(admin=u)
        resp = self.client.post(reverse('delete_student', args=[stu.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(CustomUser.objects.filter(id=u.id).exists())

    # ── Delete subject (POST required) ──
    def test_delete_subject_get_rejected(self):
        resp = self.client.get(
            reverse('delete_subject', args=[self.subject.id])
        )
        self.assertEqual(resp.status_code, 405)

    def test_delete_subject_post(self):
        sub = Subject.objects.create(
            name="Temp Sub", staff=self.staff_profile, course=self.course
        )
        resp = self.client.post(reverse('delete_subject', args=[sub.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Subject.objects.filter(id=sub.id).exists())

    # ── Check email availability ──
    def test_check_email_get_rejected(self):
        resp = self.client.get(reverse('check_email_availability'))
        self.assertEqual(resp.status_code, 405)

    def test_check_email_existing(self):
        resp = self.client.post(
            reverse('check_email_availability'),
            {'email': 'staff@test.com'}
        )
        self.assertEqual(resp.content, b'True')

    def test_check_email_available(self):
        resp = self.client.post(
            reverse('check_email_availability'),
            {'email': 'nobody@nowhere.com'}
        )
        self.assertEqual(resp.content, b'False')

    # ── Admin view attendance page ──
    def test_admin_view_attendance_page(self):
        resp = self.client.get(reverse('admin_view_attendance'))
        self.assertEqual(resp.status_code, 200)

    # ── Get admin attendance (POST) ──
    def test_get_admin_attendance_get_rejected(self):
        resp = self.client.get(reverse('get_admin_attendance'))
        self.assertEqual(resp.status_code, 405)

    def test_get_admin_attendance_success(self):
        att = Attendance.objects.create(
            session=self.session, subject=self.subject, date=date.today()
        )
        AttendanceReport.objects.create(
            student=self.student_profile, attendance=att, status=True
        )
        resp = self.client.post(reverse('get_admin_attendance'), {
            'subject': self.subject.id,
            'session': self.session.id,
            'attendance_date_id': att.id,
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['status'], 'True')

    def test_get_admin_attendance_bad_params(self):
        resp = self.client.post(reverse('get_admin_attendance'), {
            'subject': 99999,
            'session': 99999,
            'attendance_date_id': 99999,
        })
        self.assertEqual(resp.status_code, 400)

    # ── Student feedback (GET renders, POST replies) ──
    def test_student_feedback_message_get(self):
        resp = self.client.get(reverse('student_feedback_message'))
        self.assertEqual(resp.status_code, 200)

    def test_student_feedback_message_reply(self):
        fb = FeedbackStudent.objects.create(
            student=self.student_profile, feedback="Good", reply=""
        )
        resp = self.client.post(reverse('student_feedback_message'), {
            'id': fb.id, 'reply': 'Thanks!'
        })
        self.assertEqual(resp.content, b'True')
        fb.refresh_from_db()
        self.assertEqual(fb.reply, 'Thanks!')

    # ── Staff feedback ──
    def test_staff_feedback_message_get(self):
        resp = self.client.get(reverse('staff_feedback_message'))
        self.assertEqual(resp.status_code, 200)

    # ── View leave pages ──
    def test_view_student_leave_page(self):
        resp = self.client.get(reverse('view_student_leave'))
        self.assertEqual(resp.status_code, 200)

    def test_view_staff_leave_page(self):
        resp = self.client.get(reverse('view_staff_leave'))
        self.assertEqual(resp.status_code, 200)

    def test_approve_student_leave(self):
        leave = LeaveReportStudent.objects.create(
            student=self.student_profile, date=date.today(), message="Sick"
        )
        resp = self.client.post(reverse('view_student_leave'), {
            'id': leave.id, 'status': '1'
        })
        self.assertEqual(resp.content, b'True')
        leave.refresh_from_db()
        self.assertEqual(leave.status, 1)

    def test_reject_staff_leave(self):
        leave = LeaveReportStaff.objects.create(
            staff=self.staff_profile, date=date.today(), message="Travel"
        )
        resp = self.client.post(reverse('view_staff_leave'), {
            'id': leave.id, 'status': '0'
        })
        self.assertEqual(resp.content, b'True')
        leave.refresh_from_db()
        self.assertEqual(leave.status, -1)

    # ── Admin profile ──
    def test_admin_view_profile_page(self):
        resp = self.client.get(reverse('admin_view_profile'))
        self.assertEqual(resp.status_code, 200)

    # ── Notification pages ──
    def test_admin_notify_staff_page(self):
        resp = self.client.get(reverse('admin_notify_staff'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_notify_student_page(self):
        resp = self.client.get(reverse('admin_notify_student'))
        self.assertEqual(resp.status_code, 200)

    # ── Add subject page ──
    def test_add_subject_get(self):
        resp = self.client.get(reverse('add_subject'))
        self.assertEqual(resp.status_code, 200)

    def test_add_subject_post(self):
        resp = self.client.post(reverse('add_subject'), {
            'name': 'Physics',
            'course': self.course.id,
            'staff': self.staff_profile.id,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Subject.objects.filter(name='Physics').exists())

    # ── Edit staff page ──
    def test_edit_staff_get(self):
        resp = self.client.get(
            reverse('edit_staff', args=[self.staff_profile.id])
        )
        self.assertEqual(resp.status_code, 200)

    # ── Edit student page ──
    def test_edit_student_get(self):
        resp = self.client.get(
            reverse('edit_student', args=[self.student_profile.id])
        )
        self.assertEqual(resp.status_code, 200)

    # ── Edit subject ──
    def test_edit_subject_get(self):
        resp = self.client.get(
            reverse('edit_subject', args=[self.subject.id])
        )
        self.assertEqual(resp.status_code, 200)


# ═══════════════════════════════════════════════════════════════════════
#  6. STAFF VIEWS TESTS
# ═══════════════════════════════════════════════════════════════════════
class StaffViewTests(BaseTestMixin, TestCase):
    def setUp(self):
        self._setup_data()
        self.client = Client()
        self.client.login(username="staff@test.com", password="Pass1234!")

    # ── Home ──
    def test_staff_home(self):
        resp = self.client.get(reverse('staff_home'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('total_students', resp.context)

    # ── Take attendance page ──
    def test_staff_take_attendance_page(self):
        resp = self.client.get(reverse('staff_take_attendance'))
        self.assertEqual(resp.status_code, 200)

    # ── Get students (POST required) ──
    def test_get_students_get_rejected(self):
        resp = self.client.get(reverse('get_students'))
        self.assertEqual(resp.status_code, 405)

    def test_get_students_success(self):
        resp = self.client.post(reverse('get_students'), {
            'subject': self.subject.id,
            'session': self.session.id,
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data), 1)
        self.assertIn('name', data[0])

    # ── Save attendance ──
    def test_save_attendance(self):
        student_data = json.dumps([
            {'id': self.student_profile.id, 'status': 1}
        ])
        resp = self.client.post(reverse('save_attendance'), {
            'student_ids': student_data,
            'date': str(date.today()),
            'subject': self.subject.id,
            'session': self.session.id,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b'OK')
        self.assertTrue(Attendance.objects.filter(
            subject=self.subject, session=self.session
        ).exists())

    # ── Update attendance page ──
    def test_staff_update_attendance_page(self):
        resp = self.client.get(reverse('staff_update_attendance'))
        self.assertEqual(resp.status_code, 200)

    # ── Get student attendance ──
    def test_get_student_attendance(self):
        att = Attendance.objects.create(
            session=self.session, subject=self.subject, date=date.today()
        )
        AttendanceReport.objects.create(
            student=self.student_profile, attendance=att, status=True
        )
        resp = self.client.post(reverse('get_student_attendance'), {
            'attendance_date_id': att.id
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data), 1)

    # ── Update attendance ──
    def test_update_attendance(self):
        att = Attendance.objects.create(
            session=self.session, subject=self.subject, date=date.today()
        )
        report = AttendanceReport.objects.create(
            student=self.student_profile, attendance=att, status=True
        )
        student_data = json.dumps([
            {'id': self.student_user.id, 'status': 0}
        ])
        resp = self.client.post(reverse('update_attendance'), {
            'student_ids': student_data,
            'date': att.id,
        })
        self.assertEqual(resp.status_code, 200)
        report.refresh_from_db()
        self.assertFalse(report.status)

    # ── Apply leave ──
    def test_staff_apply_leave_get(self):
        resp = self.client.get(reverse('staff_apply_leave'))
        self.assertEqual(resp.status_code, 200)

    def test_staff_apply_leave_post(self):
        resp = self.client.post(reverse('staff_apply_leave'), {
            'date': '2026-03-15', 'message': 'Personal day'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(LeaveReportStaff.objects.filter(
            staff=self.staff_profile
        ).exists())

    # ── Feedback ──
    def test_staff_feedback_get(self):
        resp = self.client.get(reverse('staff_feedback'))
        self.assertEqual(resp.status_code, 200)

    def test_staff_feedback_post(self):
        resp = self.client.post(reverse('staff_feedback'), {
            'feedback': 'Need better internet'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(FeedbackStaff.objects.filter(
            staff=self.staff_profile
        ).exists())

    # ── Profile ──
    def test_staff_view_profile(self):
        resp = self.client.get(reverse('staff_view_profile'))
        self.assertEqual(resp.status_code, 200)

    # ── FCM token ──
    def test_staff_fcmtoken_get_rejected(self):
        resp = self.client.get(reverse('staff_fcmtoken'))
        self.assertEqual(resp.status_code, 405)

    def test_staff_fcmtoken_post(self):
        resp = self.client.post(reverse('staff_fcmtoken'), {
            'token': 'test-fcm-token-123'
        })
        self.assertEqual(resp.content, b'True')
        self.staff_user.refresh_from_db()
        self.assertEqual(self.staff_user.fcm_token, 'test-fcm-token-123')

    # ── Notifications ──
    def test_staff_view_notification(self):
        resp = self.client.get(reverse('staff_view_notification'))
        self.assertEqual(resp.status_code, 200)

    # ── Add result ──
    def test_staff_add_result_get(self):
        resp = self.client.get(reverse('staff_add_result'))
        self.assertEqual(resp.status_code, 200)

    def test_staff_add_result_post(self):
        resp = self.client.post(reverse('staff_add_result'), {
            'student_list': self.student_profile.id,
            'subject': self.subject.id,
            'test': 35, 'exam': 55,
        })
        self.assertEqual(resp.status_code, 200)
        result = StudentResult.objects.get(
            student=self.student_profile, subject=self.subject
        )
        self.assertEqual(result.test, 35)
        self.assertEqual(result.exam, 55)

    # ── Fetch student result ──
    def test_fetch_student_result_no_result(self):
        resp = self.client.post(reverse('fetch_student_result'), {
            'subject': self.subject.id,
            'student': self.student_profile.id,
        })
        self.assertEqual(resp.content, b'False')

    def test_fetch_student_result_exists(self):
        StudentResult.objects.create(
            student=self.student_profile, subject=self.subject,
            test=30, exam=50
        )
        resp = self.client.post(reverse('fetch_student_result'), {
            'subject': self.subject.id,
            'student': self.student_profile.id,
        })
        data = json.loads(resp.content)
        self.assertEqual(data['test'], 30)
        self.assertEqual(data['exam'], 50)

    # ── Edit result page ──
    def test_edit_student_result_get(self):
        resp = self.client.get(reverse('edit_student_result'))
        self.assertEqual(resp.status_code, 200)

    # ── Add book ──
    def test_add_book_get(self):
        resp = self.client.get(reverse('add_book'))
        self.assertEqual(resp.status_code, 200)

    def test_add_book_post_success(self):
        resp = self.client.post(reverse('add_book'), {
            'name': 'Django Unleashed',
            'author': 'Andrew Pinkham',
            'isbn': '789012',
            'category': 'Web Dev',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Book.objects.filter(name='Django Unleashed').exists())

    def test_add_book_missing_fields(self):
        resp = self.client.post(reverse('add_book'), {
            'name': '', 'author': '', 'isbn': '', 'category': ''
        })
        self.assertEqual(resp.status_code, 200)
        # Should show error, not create book
        self.assertFalse(Book.objects.filter(name='').exists())

    def test_add_book_invalid_isbn(self):
        resp = self.client.post(reverse('add_book'), {
            'name': 'Test', 'author': 'A', 'isbn': 'abc', 'category': 'X'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Book.objects.filter(name='Test').exists())

    # ── Issue book ──
    def test_issue_book_get(self):
        resp = self.client.get(reverse('issue_book'))
        self.assertEqual(resp.status_code, 200)

    def test_issue_book_post(self):
        resp = self.client.post(reverse('issue_book'), {
            'isbn2': self.book.isbn,
            'name2': self.student_profile.id,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            IssuedBook.objects.filter(
                student=self.student_profile, book=self.book
            ).exists()
        )

    # ── View issued books ──
    def test_view_issued_book(self):
        IssuedBook.objects.create(
            student=self.student_profile, book=self.book
        )
        resp = self.client.get(reverse('view_issued_book'))
        self.assertEqual(resp.status_code, 200)

    def test_view_issued_book_with_fine(self):
        """Book issued 20 days ago should incur a fine."""
        issued = IssuedBook.objects.create(
            student=self.student_profile, book=self.book
        )
        # Manually backdate issued_date (auto_now makes this tricky via ORM)
        IssuedBook.objects.filter(id=issued.id).update(
            issued_date=date.today() - timedelta(days=20)
        )
        resp = self.client.get(reverse('view_issued_book'))
        self.assertEqual(resp.status_code, 200)
        # Fine should be (20-14)*5 = 30
        details = resp.context['details']
        self.assertTrue(len(details) > 0)
        fine = details[0][4]
        self.assertEqual(fine, 30)

    def test_view_issued_book_no_book(self):
        """IssuedBook with book=None should be skipped gracefully."""
        IssuedBook.objects.create(student=self.student_profile, book=None)
        resp = self.client.get(reverse('view_issued_book'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['details']), 0)


# ═══════════════════════════════════════════════════════════════════════
#  7. STUDENT VIEWS TESTS
# ═══════════════════════════════════════════════════════════════════════
class StudentViewTests(BaseTestMixin, TestCase):
    def setUp(self):
        self._setup_data()
        self.client = Client()
        self.client.login(username="student@test.com", password="Pass1234!")

    # ── Home ──
    def test_student_home(self):
        resp = self.client.get(reverse('student_home'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('total_subject', resp.context)

    # ── View attendance page ──
    def test_student_view_attendance_get(self):
        resp = self.client.get(reverse('student_view_attendance'))
        self.assertEqual(resp.status_code, 200)

    def test_student_view_attendance_post(self):
        att = Attendance.objects.create(
            session=self.session, subject=self.subject, date=date.today()
        )
        AttendanceReport.objects.create(
            student=self.student_profile, attendance=att, status=True
        )
        resp = self.client.post(reverse('student_view_attendance'), {
            'subject': self.subject.id,
            'start_date': str(date.today() - timedelta(days=1)),
            'end_date': str(date.today() + timedelta(days=1)),
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data), 1)
        self.assertTrue(data[0]['status'])

    def test_student_view_attendance_post_bad_data(self):
        resp = self.client.post(reverse('student_view_attendance'), {
            'subject': 99999,
            'start_date': 'not-a-date',
            'end_date': 'also-not-a-date',
        })
        self.assertEqual(resp.status_code, 400)

    # ── Apply leave ──
    def test_student_apply_leave_get(self):
        resp = self.client.get(reverse('student_apply_leave'))
        self.assertEqual(resp.status_code, 200)

    def test_student_apply_leave_post(self):
        resp = self.client.post(reverse('student_apply_leave'), {
            'date': '2026-04-01', 'message': 'Family event'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(LeaveReportStudent.objects.filter(
            student=self.student_profile
        ).exists())

    # ── Feedback ──
    def test_student_feedback_get(self):
        resp = self.client.get(reverse('student_feedback'))
        self.assertEqual(resp.status_code, 200)

    def test_student_feedback_post(self):
        resp = self.client.post(reverse('student_feedback'), {
            'feedback': 'More library hours please'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(FeedbackStudent.objects.filter(
            student=self.student_profile
        ).exists())

    # ── Profile ──
    def test_student_view_profile(self):
        resp = self.client.get(reverse('student_view_profile'))
        self.assertEqual(resp.status_code, 200)

    # ── FCM token ──
    def test_student_fcmtoken_get_rejected(self):
        resp = self.client.get(reverse('student_fcmtoken'))
        self.assertEqual(resp.status_code, 405)

    def test_student_fcmtoken_post(self):
        resp = self.client.post(reverse('student_fcmtoken'), {
            'token': 'stu-fcm-token-xyz'
        })
        self.assertEqual(resp.content, b'True')
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.fcm_token, 'stu-fcm-token-xyz')

    # ── Notifications ──
    def test_student_view_notification(self):
        resp = self.client.get(reverse('student_view_notification'))
        self.assertEqual(resp.status_code, 200)

    # ── Results ──
    def test_student_view_result(self):
        StudentResult.objects.create(
            student=self.student_profile, subject=self.subject,
            test=35, exam=55
        )
        resp = self.client.get(reverse('student_view_result'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['results']), 1)

    # ── Library / View books ──
    def test_view_books(self):
        resp = self.client.get(reverse('view_books'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['books']), 1)


# ═══════════════════════════════════════════════════════════════════════
#  8. FORM VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════
class FormTests(BaseTestMixin, TestCase):
    def setUp(self):
        self._setup_data()

    def test_course_form_valid(self):
        form = CourseForm(data={'name': 'History'})
        self.assertTrue(form.is_valid())

    def test_course_form_empty(self):
        form = CourseForm(data={'name': ''})
        self.assertFalse(form.is_valid())

    def test_session_form_valid(self):
        form = SessionForm(data={
            'start_year': '2027-01-01', 'end_year': '2027-12-31'
        })
        self.assertTrue(form.is_valid())

    def test_leave_report_staff_form(self):
        form = LeaveReportStaffForm(data={
            'date': '2026-05-01', 'message': 'Holiday'
        })
        self.assertTrue(form.is_valid())

    def test_leave_report_student_form(self):
        form = LeaveReportStudentForm(data={
            'date': '2026-05-01', 'message': 'Medical'
        })
        self.assertTrue(form.is_valid())

    def test_feedback_staff_form(self):
        form = FeedbackStaffForm(data={'feedback': 'Great system'})
        self.assertTrue(form.is_valid())

    def test_feedback_student_form(self):
        form = FeedbackStudentForm(data={'feedback': 'Love it'})
        self.assertTrue(form.is_valid())

    def test_subject_form_valid(self):
        form = SubjectForm(data={
            'name': 'Chemistry',
            'staff': self.staff_profile.id,
            'course': self.course.id,
        })
        self.assertTrue(form.is_valid())

    def test_subject_form_missing_staff(self):
        form = SubjectForm(data={
            'name': 'Chemistry', 'course': self.course.id,
        })
        self.assertFalse(form.is_valid())

    def test_issue_book_form_valid(self):
        form = IssueBookForm(data={
            'isbn2': self.book.isbn,
            'name2': self.student_profile.id,
        })
        self.assertTrue(form.is_valid())

    def test_issue_book_form_invalid(self):
        form = IssueBookForm(data={'isbn2': '', 'name2': ''})
        self.assertFalse(form.is_valid())


# ═══════════════════════════════════════════════════════════════════════
#  9. CSRF PROTECTION TESTS
# ═══════════════════════════════════════════════════════════════════════
class CSRFTests(BaseTestMixin, TestCase):
    """Verify that POST endpoints enforce CSRF protection."""

    def setUp(self):
        self._setup_data()
        # Client with CSRF enforcement (no csrf-exempt shortcut)
        self.csrf_client = Client(enforce_csrf_checks=True)

    def test_delete_course_requires_csrf(self):
        self.csrf_client.login(username="hod@test.com", password="Pass1234!")
        resp = self.csrf_client.post(
            reverse('delete_course', args=[self.course.id])
        )
        self.assertEqual(resp.status_code, 403)

    def test_get_students_requires_csrf(self):
        self.csrf_client.login(username="staff@test.com", password="Pass1234!")
        resp = self.csrf_client.post(reverse('get_students'), {
            'subject': self.subject.id, 'session': self.session.id,
        })
        self.assertEqual(resp.status_code, 403)

    def test_student_fcmtoken_requires_csrf(self):
        self.csrf_client.login(username="student@test.com", password="Pass1234!")
        resp = self.csrf_client.post(
            reverse('student_fcmtoken'), {'token': 'x'}
        )
        self.assertEqual(resp.status_code, 403)

    def test_save_attendance_requires_csrf(self):
        self.csrf_client.login(username="staff@test.com", password="Pass1234!")
        resp = self.csrf_client.post(reverse('save_attendance'), {
            'student_ids': '[]', 'date': '2026-01-01',
            'subject': self.subject.id, 'session': self.session.id,
        })
        self.assertEqual(resp.status_code, 403)

    def test_check_email_requires_csrf(self):
        self.csrf_client.login(username="hod@test.com", password="Pass1234!")
        resp = self.csrf_client.post(
            reverse('check_email_availability'),
            {'email': 'test@test.com'}
        )
        self.assertEqual(resp.status_code, 403)


# ═══════════════════════════════════════════════════════════════════════
# 10. EDGE CASE & INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════
class EdgeCaseTests(BaseTestMixin, TestCase):
    def setUp(self):
        self._setup_data()
        self.client = Client()

    def test_student_home_zero_attendance(self):
        """Student with no attendance should show 0% (no DivisionByZero)."""
        self.client.login(username="student@test.com", password="Pass1234!")
        resp = self.client.get(reverse('student_home'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['percent_present'], 0)
        self.assertEqual(resp.context['percent_absent'], 0)

    def test_staff_home_no_subjects(self):
        """Staff with no assigned subjects should still render."""
        u = CustomUser.objects.create_user(
            email="newstaff@test.com", password="Pass1234!",
            user_type='2', first_name="New", last_name="Staff",
            gender="M", address="nowhere"
        )
        self.client.login(username="newstaff@test.com", password="Pass1234!")
        resp = self.client.get(reverse('staff_home'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['total_subject'], 0)

    def test_admin_home_empty_database_counts(self):
        """Admin dashboard with minimal data should not error."""
        self.client.login(username="hod@test.com", password="Pass1234!")
        resp = self.client.get(reverse('admin_home'))
        self.assertEqual(resp.status_code, 200)

    def test_view_issued_book_empty(self):
        """No issued books should render cleanly."""
        self.client.login(username="staff@test.com", password="Pass1234!")
        resp = self.client.get(reverse('view_issued_book'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['details']), 0)

    def test_delete_nonexistent_course_404(self):
        self.client.login(username="hod@test.com", password="Pass1234!")
        resp = self.client.post(reverse('delete_course', args=[99999]))
        self.assertEqual(resp.status_code, 404)

    def test_delete_nonexistent_staff_404(self):
        self.client.login(username="hod@test.com", password="Pass1234!")
        resp = self.client.post(reverse('delete_staff', args=[99999]))
        self.assertEqual(resp.status_code, 404)

    def test_get_attendance_nonexistent_subject(self):
        self.client.login(username="hod@test.com", password="Pass1234!")
        resp = self.client.post(reverse('get_attendance'), {
            'subject': 99999, 'session': self.session.id
        })
        self.assertEqual(resp.status_code, 404)

    def test_result_update_overwrites_existing(self):
        """Submitting result for same student+subject updates, not duplicates."""
        self.client.login(username="staff@test.com", password="Pass1234!")
        self.client.post(reverse('staff_add_result'), {
            'student_list': self.student_profile.id,
            'subject': self.subject.id,
            'test': 20, 'exam': 40,
        })
        self.client.post(reverse('staff_add_result'), {
            'student_list': self.student_profile.id,
            'subject': self.subject.id,
            'test': 35, 'exam': 55,
        })
        count = StudentResult.objects.filter(
            student=self.student_profile, subject=self.subject
        ).count()
        self.assertEqual(count, 1)
        r = StudentResult.objects.get(
            student=self.student_profile, subject=self.subject
        )
        self.assertEqual(r.test, 35)
        self.assertEqual(r.exam, 55)