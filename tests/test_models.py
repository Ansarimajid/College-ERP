from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date
from main_app.models import *

class CustomUserManagerTestCase(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='test@example.com', password='testpassword')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpassword'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(email='admin@example.com', password='adminpassword')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.check_password('adminpassword'))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_create_user_without_email(self):
        User = get_user_model()
        with self.assertRaises(ValidationError):
            User.objects.create_user(email='', password='testpassword')

    def test_create_user_with_invalid_email(self):
        User = get_user_model()
        with self.assertRaises(ValidationError):
            User.objects.create_user(email='invalid_email', password='testpassword')

    def test_create_superuser_with_is_staff_false(self):
        User = get_user_model()
        with self.assertRaises(AssertionError):
            User.objects.create_superuser(email='admin@example.com', password='adminpassword', is_staff=False)

    def test_create_superuser_with_is_superuser_false(self):
        User = get_user_model()
        with self.assertRaises(AssertionError):
            User.objects.create_superuser(email='admin@example.com', password='adminpassword', is_superuser=False)

class SessionModelTestCase(TestCase):
    def test_create_session(self):
        session = Session.objects.create(start_year=date(2023, 1, 1), end_year=date(2023, 12, 31))
        self.assertEqual(session.start_year, date(2023, 1, 1))
        self.assertEqual(session.end_year, date(2023, 12, 31))

    def test_create_session_with_invalid_dates(self):
        with self.assertRaises(ValidationError):
            Session.objects.create(start_year=date(2023, 12, 31), end_year=date(2023, 1, 1))

    def test_create_session_without_start_year(self):
        with self.assertRaises(IntegrityError):
            Session.objects.create(end_year=date(2023, 12, 31))

    def test_create_session_without_end_year(self):
        with self.assertRaises(IntegrityError):
            Session.objects.create(start_year=date(2023, 1, 1))

    def test_session_str_representation(self):
        session = Session.objects.create(start_year=date(2023, 1, 1), end_year=date(2023, 12, 31))
        expected_str = "From 2023-01-01 to 2023-12-31"
        self.assertEqual(str(session), expected_str)

class CustomUserModelTestCase(TestCase):
    def setUp(self):
        self.course = Course.objects.create(name='Test Course')
        self.session = Session.objects.create(start_year='2023-01-01', end_year='2023-12-31')

    def test_create_user(self):
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            user_type=1,
            gender='M',
            profile_pic=SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg"),
            address='Test Address',
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.user_type, 1)
        self.assertEqual(user.gender, 'M')
        self.assertEqual(user.address, 'Test Address')
        self.assertEqual(str(user), 'John Doe')

    def test_create_superuser(self):
        user = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
        )
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.check_password('adminpass123'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_admin_profile(self):
        user = CustomUser.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            user_type=1,
        )
        admin_profile = Admin.objects.get(admin=user)
        self.assertEqual(admin_profile.admin, user)

    def test_create_student_profile(self):
        user = CustomUser.objects.create_user(
            email='student@example.com',
            password='studentpass123',
            user_type=3,
        )
        student_profile = Student.objects.get(admin=user)
        self.assertEqual(student_profile.admin, user)
        self.assertIsNone(student_profile.course)
        self.assertIsNone(student_profile.session)

    def test_create_staff_profile(self):
        user = CustomUser.objects.create_user(
            email='staff@example.com',
            password='staffpass123',
            user_type=2,
        )
        staff_profile = Staff.objects.get(admin=user)
        self.assertEqual(staff_profile.admin, user)
        self.assertIsNone(staff_profile.course)

    def test_update_user_profile(self):
        user = CustomUser.objects.create_user(
            email='user@example.com',
            password='userpass123',
            user_type=1,
        )
        user.first_name = 'Updated'
        user.save()
        admin_profile = Admin.objects.get(admin=user)
        self.assertEqual(admin_profile.admin.first_name, 'Updated')
    
    def test_create_user_with_invalid_email(self):
        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(
                email='invalid_email',
                password='testpass123',
            )

    def test_create_user_with_empty_email(self):
        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(
                email='',
                password='testpass123',
            )

    def test_create_user_with_invalid_user_type(self):
        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(
                email='test@example.com',
                password='testpass123',
                user_type=4,
            )

    def test_create_user_with_invalid_gender(self):
        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(
                email='test@example.com',
                password='testpass123',
                gender='X',
            )

    def test_create_user_with_duplicateclea_email(self):
        CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                email='test@example.com',
                password='testpass123',
            )

    def test_create_user_profile_with_invalid_user_type(self):
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            user_type=4,
        )
        self.assertFalse(hasattr(user, 'admin'))
        self.assertFalse(hasattr(user, 'staff'))
        self.assertFalse(hasattr(user, 'student'))

    def test_update_user_profile_with_invalid_user_type(self):
        user = CustomUser.objects.create_user(
            email='user@example.com',
            password='userpass123',
            user_type=1,
        )
        user.user_type = 4
        with self.assertRaises(ValidationError):
            user.save()

class CourseModelTestCase(TestCase):
    def setUp(self):
        self.course = Course.objects.create(name='Test Course')

    def test_course_creation(self):
        self.assertEqual(self.course.name, 'Test Course')

class BookModelTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(name='Test Book', author='Test Author', isbn=1234567890, category='Test Category')

    def test_book_creation(self):
        self.assertEqual(self.book.name, 'Test Book')
        self.assertEqual(self.book.author, 'Test Author')
        self.assertEqual(self.book.isbn, 1234567890)
        self.assertEqual(self.book.category, 'Test Category')
        self.assertEqual(str(self.book), 'Test Book [1234567890]')

class LibraryModelTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.student = Student.objects.create(admin=User.objects.create_user(email='student@test.com', password='testpass'))
        self.book = Book.objects.create(name='Test Book', author='Test Author', isbn=1234567890, category='Test Category')
        self.library = Library.objects.create(student=self.student, book=self.book)

    def test_library_creation(self):
        self.assertEqual(self.library.student, self.student)
        self.assertEqual(self.library.book, self.book)
        self.assertEqual(str(self.library), str(self.student))

class IssuedBookModelTestCase(TestCase):
    def test_issued_book_creation(self):
        issued_book = IssuedBook.objects.create(student_id='123', isbn='1234567890')
        self.assertEqual(issued_book.student_id, '123')
        self.assertEqual(issued_book.isbn, '1234567890')
        self.assertEqual(issued_book.issued_date, datetime.today().date())
        self.assertEqual(issued_book.expiry_date.date(), datetime.today().date() + timedelta(days=14))

class SubjectModelTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.course = Course.objects.create(name='Test Course')
        self.staff = Staff.objects.create(admin=User.objects.create_user(email='staff@test.com', password='testpass'))
        self.subject = Subject.objects.create(name='Test Subject', staff=self.staff, course=self.course)

    def test_subject_creation(self):
        self.assertEqual(self.subject.name, 'Test Subject')
        self.assertEqual(self.subject.staff, self.staff)
        self.assertEqual(self.subject.course, self.course)
        self.assertEqual(str(self.subject), 'Test Subject')

class AttendanceModelTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.session = Session.objects.create(start_year=date(2023, 1, 1), end_year=date(2023, 12, 31))
        self.course = Course.objects.create(name='Test Course')
        self.staff = Staff.objects.create(admin=User.objects.create_user(email='staff@test.com', password='testpass'))
        self.subject = Subject.objects.create(name='Test Subject', staff=self.staff, course=self.course)
        self.attendance = Attendance.objects.create(session=self.session, subject=self.subject, date=timezone.now().date())

    def test_attendance_creation(self):
        self.assertEqual(self.attendance.session.start_year, date(2023, 1, 1))
        self.assertEqual(self.attendance.session.end_year, date(2023, 12, 31))
        self.assertEqual(self.attendance.subject, self.subject)
        self.assertEqual(self.attendance.date, timezone.now().date())

class AttendanceReportModelTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.student = Student.objects.create(admin=User.objects.create_user(email='student@test.com', password='testpass'))
        self.session = Session.objects.create(start_year='2023-01-01', end_year='2023-12-31')
        self.course = Course.objects.create(name='Test Course')
        self.staff = Staff.objects.create(admin=User.objects.create_user(email='staff@test.com', password='testpass'))
        self.subject = Subject.objects.create(name='Test Subject', staff=self.staff, course=self.course)
        self.attendance = Attendance.objects.create(session=self.session, subject=self.subject, date=timezone.now().date())
        self.attendance_report = AttendanceReport.objects.create(student=self.student, attendance=self.attendance)

    def test_attendance_report_creation(self):
        self.assertEqual(self.attendance_report.student, self.student)
        self.assertEqual(self.attendance_report.attendance, self.attendance)
        self.assertFalse(self.attendance_report.status)

class LeaveReportStudentModelTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.student = Student.objects.create(admin=User.objects.create_user(email='student@test.com', password='testpass'))
        self.leave_report_student = LeaveReportStudent.objects.create(student=self.student, date='2023-06-10', message='Test Message')

    def test_leave_report_student_creation(self):
        self.assertEqual(self.leave_report_student.student, self.student)
        self.assertEqual(self.leave_report_student.date, '2023-06-10')
        self.assertEqual(self.leave_report_student.message, 'Test Message')
        self.assertEqual(self.leave_report_student.status, 0)

class LeaveReportStaffModelTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = Staff.objects.create(admin=User.objects.create_user(email='staff@test.com', password='testpass'))
        self.leave_report_staff = LeaveReportStaff.objects.create(staff=self.staff, date='2023-06-10', message='Test Message')

    def test_leave_report_staff_creation(self):
        self.assertEqual(self.leave_report_staff.staff, self.staff)
        self.assertEqual(self.leave_report_staff.date, '2023-06-10')
        self.assertEqual(self.leave_report_staff.message, 'Test Message')
        self.assertEqual(self.leave_report_staff.status, 0)

class FeedbackStudentModelTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.student = Student.objects.create(admin=User.objects.create_user(email='student@test.com', password='testpass'))
        self.feedback_student = FeedbackStudent.objects.create(student=self.student, feedback='Test Feedback', reply='Test Reply')

    def test_feedback_student_creation(self):
        self.assertEqual(self.feedback_student.student, self.student)
        self.assertEqual(self.feedback_student.feedback, 'Test Feedback')
        self.assertEqual(self.feedback_student.reply, 'Test Reply')

class FeedbackStaffModelTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = Staff.objects.create(admin=User.objects.create_user(email='staff@test.com', password='testpass'))
        self.feedback_staff = FeedbackStaff.objects.create(staff=self.staff, feedback='Test Feedback', reply='Test Reply')

    def test_feedback_staff_creation(self):
        self.assertEqual(self.feedback_staff.staff, self.staff)
        self.assertEqual(self.feedback_staff.feedback, 'Test Feedback')
        self.assertEqual(self.feedback_staff.reply, 'Test Reply')

class NotificationStaffModelTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = Staff.objects.create(admin=User.objects.create_user(email='staff@test.com', password='testpass'))
        self.notification_staff = NotificationStaff.objects.create(staff=self.staff, message='Test Message')

    def test_notification_staff_creation(self):
        self.assertEqual(self.notification_staff.staff, self.staff)
        self.assertEqual(self.notification_staff.message, 'Test Message')

class NotificationStudentModelTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.student = Student.objects.create(admin=User.objects.create_user(email='student@test.com', password='testpass'))
        self.notification_student = NotificationStudent.objects.create(student=self.student, message='Test Message')

    def test_notification_student_creation(self):
        self.assertEqual(self.notification_student.student, self.student)
        self.assertEqual(self.notification_student.message, 'Test Message')

class StudentResultModelTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.student = Student.objects.create(admin=User.objects.create_user(email='student@test.com', password='testpass'))
        self.course = Course.objects.create(name='Test Course')
        self.staff = Staff.objects.create(admin=User.objects.create_user(email='staff@test.com', password='testpass'))
        self.subject = Subject.objects.create(name='Test Subject', staff=self.staff, course=self.course)
        self.student_result = StudentResult.objects.create(student=self.student, subject=self.subject, test=85.5, exam=92.0)

    def test_student_result_creation(self):
        self.assertEqual(self.student_result.student, self.student)
        self.assertEqual(self.student_result.subject, self.subject)
        self.assertEqual(self.student_result.test, 85.5)
        self.assertEqual(self.student_result.exam, 92.0)