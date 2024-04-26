from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from main_app.models import (
    Session,
    Subject,
    Attendance,
    Course,
    Staff,
    CustomUser,
    Student,
    Admin,
)
import json
from unittest.mock import patch


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_user(
            email="admin@test.com",
            password="adminpass",
            user_type=1,
            first_name="John",
            last_name="Doe",
            gender="M",
            profile_pic="path/to/profile/pic.jpg",
            address="Admin Address",
        )
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
        self.staff = Staff.objects.get(admin=self.staff_user)
        self.admin = Admin.objects.get(admin=self.admin_user)

        self.course = Course.objects.create(name="Test Course")
        self.subject = Subject.objects.create(
            name="Test Subject", course=self.course, staff=self.staff
        )
        self.session = Session.objects.create(
            start_year="2022-01-01", end_year="2023-12-31"
        )

    def test_login_page(self):
        response = self.client.get(reverse("login_page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main_app/login.html")

    def test_login_page_authenticated_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("login_page"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("admin_home"))

    def test_login_page_authenticated_staff(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("login_page"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("staff_home"))

    def test_login_page_authenticated_student(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("login_page"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("student_home"))

    def test_doLogin_admin(self):
        response = self.client.post(
            reverse("user_login"), {"email": "admin@test.com", "password": "adminpass"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("admin_home"))

    def test_doLogin_invalid_request_method(self):
        response = self.client.get(reverse("user_login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h4>Denied</h4>")

    def test_doLogin_staff(self):
        response = self.client.post(
            reverse("user_login"), {"email": "staff@test.com", "password": "staffpass"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("staff_home"))

    def test_doLogin_student(self):
        response = self.client.post(
            reverse("user_login"),
            {"email": "student@test.com", "password": "studentpass"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("student_home"))

    def test_doLogin_invalid(self):
        response = self.client.post(
            reverse("user_login"),
            {"email": "invalid@test.com", "password": "invalidpass"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

    def test_logout_user(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("user_logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

    def test_get_attendance(self):
        self.client.force_login(self.student_user)
        attendance = Attendance.objects.create(
            subject=self.subject, session=self.session, date="2023-06-01"
        )
        response = self.client.post(
            reverse("get_attendance"),
            {"subject": self.subject.id, "session": self.session.id},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.json())
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], attendance.id)
        self.assertEqual(data[0]["attendance_date"], str(attendance.date))
        self.assertEqual(data[0]["session"], self.session.id)

    @patch("main_app.views.get_object_or_404")
    def test_get_attendance_exception(self, mock_get_object_or_404):
        self.client.force_login(self.student_user)
        mock_get_object_or_404.side_effect = Exception("Something went wrong")
        response = self.client.post(
            reverse("get_attendance"),
            {"subject": 999, "session": 999},
            follow=True,
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Something went wrong"})

    def test_showFirebaseJS(self):
        response = self.client.get(reverse("showFirebaseJS"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_showFirebaseJS(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("showFirebaseJS"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/javascript")

    def test_login_when_invalid_user(self):
        invalid_user = CustomUser.objects.create_user(
            email="invalid@test.com",
            password="studentpass",
            user_type=4,  # invalid
            first_name="Student",
            last_name="User",
            gender="M",
            profile_pic="path/to/profile/pic.jpg",
            address="Student Address",
        )
        self.client.force_login(invalid_user)
        response = self.client.get(reverse("admin_home"))
        self.assertEqual(response.status_code, 302)
