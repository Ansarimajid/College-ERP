from django.test import TestCase
from main_app.models import *

class ModelTests(TestCase):
    def setUp(self):
        # Create test data
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='John',
            last_name='Doe',
            user_type=1,
            gender='M',
        )
        self.course = Course.objects.create(name='Test Course')
        self.student = Student.objects.create(admin=self.user, course=self.course)
        self.staff = Staff.objects.create(admin=self.user, course=self.course)
        self.subject = Subject.objects.create(name='Test Subject', staff=self.staff, course=self.course)
        self.attendance = Attendance.objects.create(subject=self.subject, date='2023-06-10')

    def test_custom_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpassword'))
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.user_type, '1')
        self.assertEqual(self.user.gender, 'M')

    def test_course_creation(self):
        self.assertEqual(self.course.name, 'Test Course')

    def test_student_creation(self):
        self.assertEqual(self.student.admin, self.user)
        self.assertEqual(self.student.course, self.course)

    def test_staff_creation(self):
        self.assertEqual(self.staff.admin, self.user)
        self.assertEqual(self.staff.course, self.course)

    def test_subject_creation(self):
        self.assertEqual(self.subject.name, 'Test Subject')
        self.assertEqual(self.subject.staff, self.staff)
        self.assertEqual(self.subject.course, self.course)

    def test_attendance_creation(self):
        self.assertEqual(self.attendance.subject, self.subject)
        self.assertEqual(str(self.attendance.date), '2023-06-10')

    def test_attendance_report_creation(self):
        attendance_report = AttendanceReport.objects.create(
            student=self.student,
            attendance=self.attendance,
            status=True
        )
        self.assertEqual(attendance_report.student, self.student)
        self.assertEqual(attendance_report.attendance, self.attendance)
        self.assertTrue(attendance_report.status)