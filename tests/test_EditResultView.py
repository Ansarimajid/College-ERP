from django.test import TestCase, Client
from django.urls import reverse
from main_app.models import (
    CustomUser,
    Staff,
    Student,
    Subject,
    StudentResult,
    Course,
    Session,
)
from main_app.forms import EditResultForm
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch


class EditResultViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
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
        self.course = Course.objects.create(name="Test Course")
        self.student_user.student.course = self.course
        self.student_user.save()
        self.subject = Subject.objects.create(
            name="Test Subject", course=self.course, staff=self.staff
        )

    def test_edit_result_get(self):
        self.client.force_login(self.staff_user)
        url = reverse("edit_student_result")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/edit_student_result.html")
        self.assertIsInstance(response.context["form"], EditResultForm)

    def test_edit_result_post_valid(self):
        self.client.force_login(self.staff_user)
        Session.objects.create(start_year="2023-01-01", end_year="2023-12-31")
        StudentResult.objects.create(
            student=self.student,
            subject=self.subject,
        )
        data = {
            "student": self.student.id,
            "subject": self.subject.id,
            "test": 80,
            "exam": 90,
            "session_year": "1",  # The first session is selected by its id which is 1
        }
        response = self.client.post(
            reverse("edit_student_result"), data=data, follow=True
        )
        self.assertEqual(StudentResult.objects.count(), 1)
        self.assertEqual(response.status_code, 200)
        result = StudentResult.objects.get(student=self.student, subject=self.subject)
        self.assertEqual(result.student, self.student)
        self.assertEqual(result.subject, self.subject)
        self.assertEqual(result.test, 80)
        self.assertEqual(result.exam, 90)

    @patch("main_app.models.StudentResult.objects.get")
    def test_edit_result_post_exception(self, mocked_save):
        mocked_save.side_effect = Exception("Database Error")
        self.client.force_login(self.staff_user)
        Session.objects.create(start_year="2023-01-01", end_year="2023-12-31")
        StudentResult.objects.create(
            student=self.student,
            subject=self.subject,
        )
        data = {
            "student": self.student.id,
            "subject": self.subject.id,
            "test": 80,
            "exam": 90,
            "session_year": "1",  # The first session is selected by its id which is 1
        }
        response = self.client.post(
            reverse("edit_student_result"), data=data, follow=True
        )
        messages = list(response.context.get("messages"))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Result Could Not Be Updated")

    def test_edit_result_post_invalid(self):
        self.client.force_login(self.staff_user)
        url = reverse("edit_student_result")
        data = {
            "student": "",
            "subject": "",
            "test": "",
            "exam": "",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/edit_student_result.html")
        self.assertIsInstance(response.context["form"], EditResultForm)
        self.assertEqual(StudentResult.objects.count(), 0)
