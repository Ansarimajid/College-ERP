from django.test import TestCase, Client
from django.urls import reverse
from main_app.models import CustomUser, Staff, Student, Subject, StudentResult, Course
from main_app.forms import EditResultForm
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile


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
        data = {
            "student": self.student.id,
            "subject": self.subject.id,
            "test": 80,
            "exam": 90,
            "session_year": "2020-03-02",
        }
        response = self.client.post(
            reverse("edit_student_result"), data=data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(StudentResult.objects.count(), 1)
        result = StudentResult.objects.first()
        self.assertEqual(result.student, self.student)
        self.assertEqual(result.subject, self.subject)
        self.assertEqual(result.test, 80)
        self.assertEqual(result.exam, 90)

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
