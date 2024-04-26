import json
from django.test import TestCase, Client
from django.urls import reverse
from main_app.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch


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
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin_home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/home_content.html")

    def test_admin_home_student(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("admin_home"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "student_template/home_content.html"
        )  # student should get redirected to student_home if they try to go to admin_home

    def test_add_staff_get(self):
        response = self.client.get(reverse("add_staff"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_staff_template.html")

    def test_add_staff_post_valid_data(self):
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
        self.assertEqual(response.status_code, 302)  # Redirect after successful POST
        self.assertEqual(
            CustomUser.objects.filter(email="newstaff@test.com").count(), 1
        )

    def test_add_staff_post_invalid_email(self):
        data = {
            "first_name": "New",
            "last_name": "Staff",
            "email": "invalidemailformat",
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            CustomUser.objects.filter(email="invalidemailformat").count(), 0
        )

    @patch("main_app.models.CustomUser.objects.create_user")
    def test_add_staff_with_exception(self, mocked_create_user):
        # Simulate an exception during user creation
        mocked_create_user.side_effect = Exception("Database Error")
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
        self.assertEqual(response.status_code, 200)
        # Check for the specific error message displayed in the template
        self.assertContains(response, "Could Not Add Database Error")
        self.assertEqual(
            CustomUser.objects.filter(email="newstaff@test.com").count(), 0
        )

    @patch("main_app.models.CustomUser.objects.create_user")
    def test_add_staff_with_exception(self, mocked_create_user):
        # Simulate an exception during user creation
        mocked_create_user.side_effect = Exception("Database Error")
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
        self.assertEqual(response.status_code, 200)
        # Check for the specific error message displayed in the template
        self.assertContains(response, "Could Not Add Database Error")
        self.assertEqual(
            CustomUser.objects.filter(email="newstaff@test.com").count(), 0
        )

    def test_add_course_get(self):
        response = self.client.get(reverse("add_course"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_course_template.html")

    def test_add_course_post_valid(self):
        data = {"name": "New Course"}
        response = self.client.post(reverse("add_course"), data=data)
        self.assertEqual(
            response.status_code, 302
        )  # Check for redirect after successful POST
        self.assertEqual(Course.objects.filter(name="New Course").count(), 1)

    def test_add_course_post_invalid(self):
        data = {}
        response = self.client.post(reverse("add_course"), data=data)
        self.assertEqual(
            response.status_code, 200
        )  # Remains on the same page due to error
        self.assertEqual(Course.objects.filter(name="").count(), 0)

    @patch("main_app.models.Course.save")
    def test_add_course_with_exception(self, mocked_save):
        mocked_save.side_effect = Exception("Database Error")
        data = {"name": "New Course"}
        response = self.client.post(reverse("add_course"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Could Not Add")
        self.assertEqual(Course.objects.filter(name="New Course").count(), 0)

    def test_manage_views(self):
        # Test manage_staff
        response = self.client.get(reverse("manage_staff"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/manage_staff.html")

    def test_edit_staff_get(self):
        response = self.client.get(reverse("edit_staff", args=[self.staff.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_staff_template.html")

    def test_edit_staff_post_with_password(self):
        data = {
            "first_name": "New Staff",
            "last_name": "User",
            "email": "staff@test.com",
            "password": "staffpass",
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

    def test_edit_staff_post_without_password(self):
        data_without_password = {
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
            reverse("edit_staff", args=[self.staff.id]), data=data_without_password
        )
        self.assertEqual(response.status_code, 302)
        self.staff_user.refresh_from_db()
        self.assertEqual(self.staff_user.first_name, "New Staff")

    # Fault: no validation to enforce that start date is before end date
    def test_edit_staff_post_invalid_email(self):
        data = {
            "first_name": "New Staff",
            "last_name": "User",
            "email": "invalidemail",
            "password": "staffpass",
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
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_staff_template.html")
        self.assertFormError(response, "form", "email", "Enter a valid email address.")
        messages = list(response.context.get("messages"))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Please fill form properly")

    def test_email_exists(self):
        data = {"email": "student@test.com"}
        response = self.client.post(reverse("check_email_availability"), data=data)
        self.assertEqual(response.content, b"True")

    def test_email_does_not_exist(self):
        data = {"email": "nonexistent@email.com"}
        response = self.client.post(reverse("check_email_availability"), data=data)
        self.assertEqual(response.content, b"False")

    def test_student_feedback_message_get(self):
        response = self.client.get(reverse("student_feedback_message"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/student_feedback_template.html")

    def test_student_feedback_message_post(self):
        feedback = FeedbackStudent.objects.create(
            student=self.student, feedback="Test feedback"
        )
        data = {"id": feedback.id, "reply": "Test reply"}
        response = self.client.post(reverse("student_feedback_message"), data=data)
        self.assertEqual(response.content, b"True")
        feedback.refresh_from_db()
        self.assertEqual(feedback.reply, "Test reply")

    def test_view_student_leave_get(self):
        response = self.client.get(reverse("view_student_leave"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/student_leave_view.html")

    def test_view_student_leave_post_approve(self):
        leave = LeaveReportStudent.objects.create(
            student=self.student, date="2023-06-10", message="Test leave"
        )
        data = {"id": leave.id, "status": "1"}
        response = self.client.post(reverse("view_student_leave"), data=data)
        self.assertEqual(response.content, b"True")
        leave.refresh_from_db()
        self.assertEqual(leave.status, 1)

    def test_view_student_leave_post_disapprove(self):
        leave = LeaveReportStudent.objects.create(
            student=self.student, date="2023-06-10", message="Test leave"
        )
        data = {"id": leave.id, "status": "2"}
        response = self.client.post(reverse("view_student_leave"), data=data)
        self.assertEqual(response.content, b"True")
        leave.refresh_from_db()
        self.assertEqual(leave.status, -1)

    def test_admin_view_attendance(self):
        response = self.client.get(reverse("admin_view_attendance"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/admin_view_attendance.html")

    def test_admin_view_profile_get(self):
        response = self.client.get(reverse("admin_view_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/admin_view_profile.html")

    def test_admin_view_profile_post_valid(self):
        data = {
            "first_name": "Admin",
            "last_name": "User Updated",
            "email": "newadmin@test.com",
            "gender": "M",
            "address": "moon",
            "profile_pic": SimpleUploadedFile(
                "small.gif",
                small_gif,
                content_type="image/gif",
            ),
        }
        response = self.client.post(
            reverse("admin_view_profile"), data=data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/admin_view_profile.html")

    def test_admin_notify_staff_get(self):
        response = self.client.get(reverse("admin_notify_staff"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/staff_notification.html")

    def test_admin_notify_student_get(self):
        response = self.client.get(reverse("admin_notify_student"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/student_notification.html")

    def test_send_staff_notification_post(self):
        data = {"id": self.staff.admin.id, "message": "Test notification"}
        response = self.client.post(reverse("send_staff_notification"), data=data)
        self.assertEqual(response.content, b"True")
        self.assertEqual(NotificationStaff.objects.count(), 1)

    def test_send_student_notification_post(self):
        data = {"id": self.student.admin.id, "message": "Test notification"}
        response = self.client.post(reverse("send_student_notification"), data=data)
        self.assertEqual(response.content, b"True")
        self.assertEqual(NotificationStudent.objects.count(), 1)

    def test_delete_staff(self):
        self.assertEqual(CustomUser.objects.filter(staff__id=self.staff.id).count(), 1)
        response = self.client.get(reverse("delete_staff", args=[self.staff.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CustomUser.objects.filter(staff__id=self.staff.id).count(), 0)

    def test_delete_student(self):
        self.assertEqual(
            CustomUser.objects.filter(student__id=self.student.id).count(), 1
        )
        response = self.client.get(reverse("delete_student", args=[self.student.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            CustomUser.objects.filter(student__id=self.student.id).count(), 0
        )

    def test_delete_course(self):
        self.assertEqual(Course.objects.filter(id=self.course.id).count(), 1)
        response = self.client.get(reverse("delete_course", args=[self.course.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Course.objects.filter(id=self.course.id).count(), 0)

    def test_delete_session(self):
        self.assertEqual(Session.objects.filter(id=self.session.id).count(), 1)
        response = self.client.get(reverse("delete_session", args=[self.session.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Session.objects.filter(id=self.session.id).count(), 0)

    def test_edit_student_get(self):
        response = self.client.get(reverse("edit_student", args=[self.student.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_student_template.html")

    def test_edit_student_post_without_password(self):
        data_without_password = {
            "first_name": "Updated Student",
            "last_name": "User",
            "email": "student@test.com",
            "gender": "M",
            "course": self.course.id,
            "session": self.session.id,
            "address": "moon",
            "profile_pic": SimpleUploadedFile(
                "small.gif",
                small_gif,
                content_type="image/gif",
            ),
        }
        response = self.client.post(
            reverse("edit_student", args=[self.student.id]), data=data_without_password
        )
        self.assertEqual(response.status_code, 302)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.first_name, "Updated Student")

    def test_edit_student_post_with_password(self):
        data_with_password = {
            "first_name": "Updated Student 2",
            "last_name": "User",
            "email": "student@test.com",
            "password": "studentpass",
            "gender": "M",
            "course": self.course.id,
            "session": self.session.id,
            "address": "moon",
            "profile_pic": SimpleUploadedFile(
                "small.gif",
                small_gif,
                content_type="image/gif",
            ),
        }
        response = self.client.post(
            reverse("edit_student", args=[self.student.id]), data=data_with_password
        )
        self.assertEqual(response.status_code, 302)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.first_name, "Updated Student 2")

    # Fault: no validation to enforce that start date is before end date
    def test_edit_student_post_invalid_email(self):
        data_with_password = {
            "first_name": "Updated Student 2",
            "last_name": "User",
            "email": "invalidemail",
            "password": "studentpass",
            "gender": "M",
            "course": self.course.id,
            "session": self.session.id,
            "address": "moon",
            "profile_pic": SimpleUploadedFile(
                "small.gif",
                small_gif,
                content_type="image/gif",
            ),
        }
        response = self.client.post(
            reverse("edit_student", args=[self.student.id]), data=data_with_password
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_student_template.html")
        self.assertFormError(response, "form", "email", "Enter a valid email address.")

    def test_edit_course_get(self):
        response = self.client.get(reverse("edit_course", args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_course_template.html")

    def test_edit_course_post_valid(self):
        data = {"name": "Updated Course"}
        response = self.client.post(
            reverse("edit_course", args=[self.course.id]), data=data, follow=True
        )
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Updated Course")

    def test_edit_course_post_invalid(self):
        data = {"name": ""}
        response = self.client.post(
            reverse("edit_course", args=[self.course.id]), data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_course_template.html")
        self.assertFormError(response, "form", "name", "This field is required.")

    def test_edit_subject_get(self):
        response = self.client.get(reverse("edit_subject", args=[self.subject.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_subject_template.html")

    def test_edit_subject_post_valid(self):
        data = {
            "name": "Updated Subject",
            "course": self.course.id,
            "staff": self.staff.id,
        }
        response = self.client.post(
            reverse("edit_subject", args=[self.subject.id]), data=data
        )
        self.assertEqual(response.status_code, 302)
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.name, "Updated Subject")

    def test_edit_subject_post_invalid(self):
        data = {"name": "", "course": self.course.id, "staff": self.staff.id}
        response = self.client.post(
            reverse("edit_subject", args=[self.subject.id]), data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_subject_template.html")
        self.assertFormError(response, "form", "name", "This field is required.")

    def test_edit_session_get_request(self):
        response = self.client.get(reverse("edit_session", args=[self.session.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_session_template.html")

    def test_edit_session_post_request_with_valid_data(self):
        data = {"start_year": "2023-01-01", "end_year": "2024-12-31"}
        response = self.client.post(
            reverse("edit_session", args=[self.session.id]), data=data
        )
        self.assertEqual(response.status_code, 302)
        self.session.refresh_from_db()
        self.assertEqual(str(self.session.start_year), "2023-01-01")
        self.assertEqual(str(self.session.end_year), "2024-12-31")

    # Fault: no validation to enforce that start date is before end date
    def test_edit_session_post_request_with_invalid_data(self):
        data = {"start_year": "2024-01-01", "end_year": "2023-12-31"}
        response = self.client.post(
            reverse("edit_session", args=[self.session.id]), data=data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_session_template.html")
        self.assertFormError(
            response, "form", None, "Start date should be before end date."
        )

    def test_add_student_get(self):
        response = self.client.get(reverse("add_student"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_student_template.html")

    def test_add_student_post_valid(self):
        data = {
            "first_name": "New",
            "last_name": "Student",
            "email": "newstudent@test.com",
            "password": "newstudentpass",
            "gender": "M",
            "course": self.course.id,
            "session": self.session.id,
            "address": "moon",
            "profile_pic": SimpleUploadedFile(
                "small.gif",
                small_gif,
                content_type="image/gif",
            ),
        }
        self.client.post(reverse("add_student"), data=data)
        self.assertEqual(
            CustomUser.objects.filter(email="newstudent@test.com").count(), 1
        )

    def test_add_student_post_invalid(self):
        data = {
            "first_name": "New",
            "last_name": "Student",
            "email": "invalidemailformat",  # Invalid email
            "password": "newstudentpass",
            "gender": "M",
            "course": self.course.id,
            "session": self.session.id,
            "address": "moon",
            "profile_pic": SimpleUploadedFile(
                "small.gif",
                small_gif,
                content_type="image/gif",
            ),
        }
        response = self.client.post(reverse("add_student"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            CustomUser.objects.filter(email="invalidemailformat").count(), 0
        )

    @patch("main_app.models.CustomUser.objects.create_user")
    def test_add_student_with_exception(self, mocked_create_user):
        mocked_create_user.side_effect = Exception("Database Error")
        data = {
            "first_name": "New",
            "last_name": "Student",
            "email": "newstudent@test.com",
            "password": "newstudentpass",
            "gender": "M",
            "course": self.course.id,
            "session": self.session.id,
            "address": "moon",
            "profile_pic": SimpleUploadedFile(
                "small.gif",
                small_gif,
                content_type="image/gif",
            ),
        }
        response = self.client.post(reverse("add_student"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Could Not Add: Database Error")
        self.assertEqual(
            CustomUser.objects.filter(email="newstudent@test.com").count(), 0
        )

    def test_add_subject_get(self):
        response = self.client.get(reverse("add_subject"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_subject_template.html")

    def test_add_subject_post_valid(self):
        data = {
            "name": "New Subject",
            "course": self.course.id,
            "staff": self.staff.id,
        }
        response = self.client.post(reverse("add_subject"), data=data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful POST
        self.assertEqual(Subject.objects.filter(name="New Subject").count(), 1)

    def test_add_subject_post_invalid(self):
        data = {"name": "", "course": self.course.id, "staff": self.staff.id}
        response = self.client.post(reverse("add_subject"), data=data)
        self.assertEqual(response.status_code, 200)  # Should stay on the same page
        self.assertTemplateUsed(response, "hod_template/add_subject_template.html")

    @patch("main_app.models.Subject.save")
    def test_add_subject_with_exception(self, mocked_save):
        mocked_save.side_effect = Exception("Database Error")
        data = {"name": "New Subject", "course": self.course.id, "staff": self.staff.id}

        response = self.client.post(reverse("add_subject"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Could Not Add Database Error")
        self.assertEqual(Subject.objects.filter(name="New Subject").count(), 0)

    def test_manage_student(self):
        response = self.client.get(reverse("manage_student"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/manage_student.html")

    def test_manage_course(self):
        response = self.client.get(reverse("manage_course"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/manage_course.html")

    def test_manage_subject(self):
        response = self.client.get(reverse("manage_subject"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/manage_subject.html")

    def test_add_session_get(self):
        response = self.client.get(reverse("add_session"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_session_template.html")

    def test_add_session_post_valid(self):
        data = {"start_year": "2024-01-01", "end_year": "2025-12-31"}
        response = self.client.post(reverse("add_session"), data=data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful POST
        self.assertEqual(
            Session.objects.filter(
                start_year="2024-01-01", end_year="2025-12-31"
            ).count(),
            1,
        )

    def test_add_session_post_invalid(self):
        data = {"start_year": "2025-01-01", "end_year": "2024-12-31"}
        response = self.client.post(reverse("add_session"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)  # Should stay on the same page
        self.assertTemplateUsed(response, "hod_template/add_session_template.html")

    def test_manage_session(self):
        response = self.client.get(reverse("manage_session"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/manage_session.html")

    def test_staff_feedback_message_get(self):
        response = self.client.get(reverse("staff_feedback_message"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/staff_feedback_template.html")

    def test_staff_feedback_message_post(self):
        feedback = FeedbackStaff.objects.create(
            staff=self.staff, feedback="Staff test feedback"
        )
        data = {"id": feedback.id, "reply": "Reply to staff feedback"}
        response = self.client.post(reverse("staff_feedback_message"), data=data)
        self.assertEqual(response.content, b"True")  # Check for successful response
        feedback.refresh_from_db()
        self.assertEqual(feedback.reply, "Reply to staff feedback")

    def test_view_staff_leave_get(self):
        response = self.client.get(reverse("view_staff_leave"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/staff_leave_view.html")

    def test_view_staff_leave_post_approve(self):
        leave = LeaveReportStaff.objects.create(
            staff=self.staff, date="2023-07-01", message="Test leave for staff"
        )
        data = {"id": leave.id, "status": "1"}
        response = self.client.post(reverse("view_staff_leave"), data=data)
        self.assertEqual(response.content, b"True")  # Check for successful response
        leave.refresh_from_db()
        self.assertEqual(leave.status, 1)  # Check if leave is approved

    def test_view_staff_leave_post_disapprove(self):
        leave = LeaveReportStaff.objects.create(
            staff=self.staff, date="2023-07-01", message="Test leave for staff"
        )
        data = {"id": leave.id, "status": "2"}
        response = self.client.post(reverse("view_staff_leave"), data=data)
        self.assertEqual(response.content, b"True")  # Check for successful response
        leave.refresh_from_db()
        self.assertEqual(leave.status, -1)  # Check if leave is disapproved

    def test_get_admin_attendance(self):
        attendance = Attendance.objects.create(
            subject=self.subject, session=self.session, date="2023-07-15"
        )
        AttendanceReport.objects.create(
            attendance=attendance, student=self.student, status=True
        )

        data = {
            "subject": self.subject.id,
            "session": self.session.id,
            "attendance_date_id": attendance.id,
        }
        response = self.client.post(reverse("get_admin_attendance"), data=data)
        response_list = json.loads(response.json())

        self.assertIsInstance(response_list, list)
        self.assertEqual(
            len(response_list), 1
        )  # Check if one attendance record is returned
        self.assertEqual(response_list[0]["status"], "True")  # Check attendance status
        self.assertEqual(
            response_list[0]["name"], str(self.student)
        )  # Check student name

    def test_delete_subject(self):
        response = self.client.get(reverse("delete_subject", args=[self.subject.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Subject.objects.filter(id=self.subject.id).count(), 0)

    # Fault: no HttpResponse returned for an exception
    @patch("main_app.models.Student.save")
    def test_edit_student_with_exception(self, mocked_save):
        mocked_save.side_effect = Exception("Database Error")
        data = {
            "first_name": "Updated",
            "last_name": "Student",
            "email": "student@test.com",
            "gender": "M",
            "course": self.course.id,
            "session": self.session.id,
            "address": "Update Address",
            "profile_pic": SimpleUploadedFile(
                "updated.gif",
                small_gif,  # Assume small_gif is defined elsewhere in your test class
                content_type="image/gif",
            ),
        }
        response = self.client.post(
            reverse("edit_student", args=[self.student.id]), data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Could Not Update")

    @patch("main_app.models.Course.save")
    def test_edit_course_with_exception(self, mocked_save):
        mocked_save.side_effect = Exception("Database Error")
        data = {"name": "Updated Course"}
        response = self.client.post(
            reverse("edit_course", args=[self.course.id]), data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Could Not Update")

    # Fault: Exception not propagated
    @patch("main_app.models.Subject.save")
    def test_edit_subject_with_exception(self, mocked_save):
        mocked_save.side_effect = Exception("Database Error")
        data = {
            "name": "Updated Subject",
            "course": self.course.id,
            "staff": self.staff.id,
        }
        response = self.client.post(
            reverse("edit_subject", args=[self.subject.id]), data=data
        )
        self.assertEqual(response.status_code, 200)
        print(response)
        self.assertContains(response, "Could Not Update")

    @patch("main_app.models.Session.save")
    def test_edit_session_with_exception(self, mocked_save):
        mocked_save.side_effect = Exception("Database Error")
        data = {"start_year": "2023-01-02", "end_year": "2024-12-31"}
        response = self.client.post(
            reverse("edit_session", args=[self.session.id]), data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Session Could Not Be Updated")

    @patch("main_app.models.Session.save")
    def test_add_session_with_exception(self, mocked_save):
        mocked_save.side_effect = Exception("Database Error")
        data = {"start_year": "2023-01-02", "end_year": "2024-12-31"}
        response = self.client.post(reverse("add_session"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Could Not Add")

    @patch("main_app.models.CustomUser.objects.filter")
    def test_check_email_availability_with_exception(self, mocked_filter):
        mocked_filter.side_effect = Exception("Database Error")
        data = {"email": "existing@email.com"}
        response = self.client.post(reverse("check_email_availability"), data=data)
        self.assertEqual(response.content.decode(), "False")

    # Fault: no HttpResponse returned for an Exception
    @patch("main_app.models.AttendanceReport.objects.filter")
    def test_get_admin_attendance_with_exception(self, mocked_filter):
        mocked_filter.side_effect = Exception("Database Error")
        attendance = Attendance.objects.create(
            subject=self.subject, session=self.session, date="2023-07-15"
        )
        data = {
            "subject": self.subject.id,
            "session": self.session.id,
            "attendance_date_id": attendance.id,
        }
        response = self.client.post(reverse("get_admin_attendance"), data=data)
        self.assertIsNone(response.json())

    @patch("main_app.models.CustomUser.save")
    def test_admin_view_profile_with_exception(self, mocked_save):
        mocked_save.side_effect = Exception("Database Error")
        data = {
            "first_name": "Admin",
            "last_name": "User Updated",
            "email": "newadmin@test.com",
            "gender": "M",
            "address": "moon",
            "profile_pic": SimpleUploadedFile(
                "small.gif",
                small_gif,
                content_type="image/gif",
            ),
        }
        response = self.client.post(
            reverse("admin_view_profile"), data=data, follow=True
        )
        self.assertContains(response, "Error Occured While Updating Profile")

    @patch("requests.post")
    def test_send_student_notification_with_exception(self, mocked_post):
        mocked_post.side_effect = Exception("Network Error")
        data = {"id": self.student.admin.id, "message": "Test Notification"}
        response = self.client.post(reverse("send_student_notification"), data=data)
        self.assertEqual(response.content.decode(), "False")

    @patch("requests.post")
    def test_send_staff_notification_with_exception(self, mocked_post):
        mocked_post.side_effect = Exception("Network Error")
        data = {"id": self.staff.admin.id, "message": "Test Notification"}
        response = self.client.post(reverse("send_staff_notification"), data=data)
        self.assertEqual(response.content.decode(), "False")

    @patch("main_app.models.Course.delete")
    def test_delete_course_with_exception(self, mocked_delete):
        mocked_delete.side_effect = Exception("Database Error")
        response = self.client.get(
            reverse("delete_course", args=[self.course.id]), follow=True
        )
        self.assertContains(
            response, "Sorry, some students are assigned to this course already."
        )

    @patch("main_app.models.Session.delete")
    def test_delete_session_with_exception(self, mocked_delete):
        mocked_delete.side_effect = Exception("Database Error")
        response = self.client.get(
            reverse("delete_session", args=[self.session.id]), follow=True
        )
        self.assertContains(response, "There are students assigned to this session.")
