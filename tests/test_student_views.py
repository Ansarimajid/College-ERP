from django.test import TestCase, Client
from django.urls import reverse
from main_app.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
import json


class StudentViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_user = CustomUser.objects.create_user(
            email="student@test.com",
            password="studentpass",
            user_type=3,
            first_name="Student",
            last_name="User",
            gender="M",
            profile_pic="path/to/profile/pic.jpg",
            address="Student Address",
        )
        self.student = Student.objects.get(admin=self.student_user)
        self.staff_user = CustomUser.objects.create_user(
            email="staff@test.com",
            password="staffpass",
            user_type=2,
            first_name="Staff",
            last_name="User",
            gender="M",
            profile_pic="path/to/profile/pic.jpg",
            address="Staff Address",
        )
        self.staff = Staff.objects.get(admin=self.staff_user)
        self.course = Course.objects.create(name="Test Course")
        self.subject = Subject.objects.create(
            name="Test Subject", course=self.course, staff=self.staff
        )
        self.session = Session.objects.create(
            start_year="2022-01-01", end_year="2023-12-31"
        )

    def test_student_home(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("student_home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_template/home_content.html")

    def test_student_home_with_attendance(self):
        self.client.force_login(self.student_user)
        attendance = Attendance.objects.create(
            subject=self.subject, date="2023-07-01", session=self.session
        )
        AttendanceReport.objects.create(
            student=self.student, attendance=attendance, status=True
        )

        response = self.client.get(reverse("student_home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_template/home_content.html")

        self.assertNotEqual(response.context["total_attendance"], 0)
        self.assertEqual(response.context["percent_present"], 100)
        self.assertEqual(response.context["percent_absent"], 0)

    def test_student_view_attendance(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("student_view_attendance"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "student_template/student_view_attendance.html"
        )

    def test_student_view_attendance_post(self):
        self.client.force_login(self.student_user)
        attendance = Attendance.objects.create(
            session=self.session, subject=self.subject, date="2023-07-01"
        )
        AttendanceReport.objects.create(
            student=self.student, attendance=attendance, status=True
        )

        data = {
            "subject": self.subject.id,
            "start_date": "2023-07-01",
            "end_date": "2023-07-02",
        }
        response = self.client.post(reverse("student_view_attendance"), data=data)
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.json())
        self.assertEqual(len(json_data), 1)
        self.assertEqual(json_data[0]["status"], True)

    def test_student_apply_leave(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("student_apply_leave"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_template/student_apply_leave.html")

    def test_student_apply_leave_post(self):
        self.client.force_login(self.student_user)
        data = {"date": "2023-07-01", "message": "Test leave application"}
        response = self.client.post(reverse("student_apply_leave"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            LeaveReportStudent.objects.filter(student=self.student).count(), 1
        )

    def test_student_feedback(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("student_feedback"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_template/student_feedback.html")

    def test_student_feedback_post(self):
        self.client.force_login(self.student_user)
        data = {"feedback": "Test feedback"}
        response = self.client.post(reverse("student_feedback"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            FeedbackStudent.objects.filter(student=self.student).count(), 1
        )

    def test_student_view_profile(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("student_view_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_template/student_view_profile.html")

    def test_student_view_profile_post(self):
        self.client.force_login(self.student_user)
        data = {
            "email": "student@test.com",
            "first_name": "Updated Student",
            "last_name": "User",
            "password": "newpassword",
            "address": "Updated Address",
            "gender": "F",
        }
        response = self.client.post(
            reverse("student_view_profile"), data=data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.first_name, "Updated Student")

    def test_student_fcmtoken(self):
        self.client.force_login(self.student_user)
        data = {"token": "test_token"}
        response = self.client.post(reverse("student_fcmtoken"), data=data)
        self.assertEqual(response.status_code, 200)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.fcm_token, "test_token")

    def test_student_view_notification(self):
        self.client.force_login(self.student_user)
        NotificationStudent.objects.create(
            student=self.student, message="Test notification"
        )
        response = self.client.get(reverse("student_view_notification"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "student_template/student_view_notification.html"
        )

    def test_student_view_result(self):
        self.client.force_login(self.student_user)
        StudentResult.objects.create(
            student=self.student, subject=self.subject, exam=80, test=90
        )
        response = self.client.get(reverse("student_view_result"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_template/student_view_result.html")

    def test_view_books(self):
        self.client.force_login(self.student_user)
        Book.objects.create(
            name="Test Book",
            author="Test Author",
            isbn=1234567890,
            category="Test Category",
        )
        response = self.client.get(reverse("view_books"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_template/view_books.html")