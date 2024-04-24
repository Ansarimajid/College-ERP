from django.test import TestCase, Client
from django.urls import reverse
from main_app.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
import os

small_gif = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
    b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
    b"\x02\x4c\x01\x00\x3b"
)


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_user(
            email="admin@test.com",
            password="Admin",
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
        self.course = Course.objects.create(name="Test Course")
        self.staff = Staff.objects.get(admin=self.staff_user)
        self.admin = Admin.objects.get(admin=self.admin_user)

        # Create subject and session
        self.subject = Subject.objects.create(
            name="Test Subject", course=self.course, staff=self.staff
        )
        self.session = Session.objects.create(
            start_year="2022-01-01", end_year="2023-12-31"
        )

        self.user, _ = CustomUser.objects.get_or_create(
            email="student@student.com", password="student@erp"
        )
        self.client.force_login(self.user)

    def test_admin_home(self):
        response = self.client.get(reverse("admin_home"))
        self.assertEqual(response.status_code, 200)

    def test_add_staff(self):
        response = self.client.get(reverse("add_staff"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_staff_template.html")

        # Test POST request with valid data
        data = {
            "first_name": "New",
            "last_name": "Staff",
            "email": "newstaff@test.com",
            "password": "newstaffpass",
            "gender": "M",
            "course": self.course.id,
            "address": "moon",
            "profile_pic": SimpleUploadedFile(
                "small.gif",
                small_gif,
                content_type="image/gif",
            ),
        }
        response = self.client.post(reverse("add_staff"), data=data)
        self.assertEqual(
            CustomUser.objects.filter(email="newstaff@test.com").count(), 1
        )

        # Test POST request with invalid data
        data["email"] = "invalidemailformat"
        response = self.client.post(reverse("add_staff"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            CustomUser.objects.filter(email="invalidemailformat").count(), 0
        )

    def test_add_course(self):
        # Test GET request
        response = self.client.get(reverse("add_course"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_course_template.html")

        # Test POST request with valid data
        data = {"name": "New Course"}
        response = self.client.post(reverse("add_course"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Course.objects.filter(name="New Course").count(), 1)

        # Test POST request with invalid data
        data = {}
        response = self.client.post(reverse("add_course"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Course.objects.filter(name="").count(), 0)

    def test_manage_views(self):
        # Test manage_staff
        response = self.client.get(reverse("manage_staff"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/manage_staff.html")

        # Test manage_student, manage_course, manage_subject, manage_session
        # Similar to manage_staff

    def test_edit_views(self):
        # Test edit_staff with GET
        response = self.client.get(reverse("edit_staff", args=[self.staff.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_staff_template.html")

        # Test edit_staff with POST and valid data
        data = {
            "first_name": "New Staff",
            "last_name": "User",
            "email": "staff@test.com",
            "gender": "M",
            "course": self.course.id,
            "address": "moon",
            "profile_pic": SimpleUploadedFile(
                "small.gif",
                small_gif,
                content_type="image/gif",
            ),
        }
        response = self.client.post(
            reverse("edit_staff", args=[self.staff.id]), data=data
        )
        self.assertEqual(response.status_code, 302)
        self.staff_user.refresh_from_db()
        self.assertEqual(self.staff_user.first_name, "New Staff")

        # Test edit_staff with POST and invalid data
        # data["email"] = "invalidemail"
        # response = self.client.post(
        #     reverse("edit_staff", args=[self.staff.id]), data=data
        # )
        # self.assertEqual(response.status_code, 200)

        # Test edit_student, edit_course, edit_subject, edit_session
        # Similar to edit_staff

    def test_check_email_availability(self):
        # Test email already exists
        data = {"email": "student@test.com"}
        response = self.client.post(reverse("check_email_availability"), data=data)
        self.assertEqual(response.content, b"True")

        # Test email does not exist
        data = {"email": "nonexistent@email.com"}
        response = self.client.post(reverse("check_email_availability"), data=data)
        self.assertEqual(response.content, b"False")

    def test_feedback_views(self):
        # Test student_feedback_message GET
        response = self.client.get(reverse("student_feedback_message"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/student_feedback_template.html")

        # Test student_feedback_message POST
        feedback = FeedbackStudent.objects.create(
            student=self.student, feedback="Test feedback"
        )
        data = {"id": feedback.id, "reply": "Test reply"}
        response = self.client.post(reverse("student_feedback_message"), data=data)
        self.assertEqual(response.content, b"True")
        feedback.refresh_from_db()
        self.assertEqual(feedback.reply, "Test reply")

        # Test staff_feedback_message
        # Similar to student_feedback_message

    def test_leave_views(self):
        # Test view_student_leave GET
        response = self.client.get(reverse("view_student_leave"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/student_leave_view.html")

        # Test view_student_leave POST approve
        leave = LeaveReportStudent.objects.create(
            student=self.student, date="2023-06-10", message="Test leave"
        )
        data = {"id": leave.id, "status": "1"}
        response = self.client.post(reverse("view_student_leave"), data=data)
        self.assertEqual(response.content, b"True")
        leave.refresh_from_db()
        self.assertEqual(leave.status, 1)

        # Test view_student_leave POST disapprove
        data = {"id": leave.id, "status": "2"}
        response = self.client.post(reverse("view_student_leave"), data=data)
        self.assertEqual(response.content, b"True")
        leave.refresh_from_db()
        self.assertEqual(leave.status, -1)

        # Test view_staff_leave
        # Similar to view_student_leave

    def test_admin_view_attendance(self):
        response = self.client.get(reverse("admin_view_attendance"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/admin_view_attendance.html")

    def test_admin_view_profile(self):
        # Test GET request
        response = self.client.get(reverse("admin_view_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/admin_view_profile.html")

        # Test POST request with valid data
        data = {
            "first_name": "Admin",
            "last_name": "User Updated",
            "email": "admin@test.com",
            "gender": "M",
            "address": "moon",
            "profile_pic": SimpleUploadedFile(
                "small.gif",
                small_gif,
                content_type="image/gif",
            ),
        }
        response = self.client.post(reverse("admin_view_profile"), data=data)
        updated_admin = CustomUser.objects.get(email="admin@test.com")
        # self.assertEqual(updated_admin.last_name, "User Updated")
        # Test POST request with invalid data
        data["email"] = "invalidemail"
        response = self.client.post(reverse("admin_view_profile"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/admin_view_profile.html")

    # Additional tests for notification views, delete views
