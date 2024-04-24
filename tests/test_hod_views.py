import json
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

    def test_edit_staff(self):
        # Test edit_staff with GET
        response = self.client.get(reverse("edit_staff", args=[self.staff.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_staff_template.html")

        # Test edit_staff with POST and password exists
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
        # self.assertEqual(self.staff_user.password, "staffpass")

        # Test edit_staff with POST and password doesn't exist
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

        # Test edit_staff with POST and invalid email
        data["email"] = "invalidemail"
        response = self.client.post(
            reverse("edit_staff", args=[self.staff.id]), data=data
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_staff_template.html")
        self.assertFormError(response, "form", "email", "Enter a valid email address.")

        # Check if the error message is displayed
        messages = list(response.context.get("messages"))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Please fill form properly")

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
        # updated_admin = CustomUser.objects.get(email="admin@test.com")
        # self.assertEqual(updated_admin.last_name, "User Updated")
        # Test POST request with invalid data
        # data["email"] = "invalidemail"
        # response = self.client.post(reverse("admin_view_profile"), data=data)
        # self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, "hod_template/admin_view_profile.html")

    def test_notification_views(self):
        # Test admin_notify_staff GET
        response = self.client.get(reverse("admin_notify_staff"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/staff_notification.html")

        # Test admin_notify_student GET
        response = self.client.get(reverse("admin_notify_student"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/student_notification.html")

        # Test send_staff_notification POST
        data = {"id": self.staff.admin.id, "message": "Test notification"}
        response = self.client.post(reverse("send_staff_notification"), data=data)
        self.assertEqual(response.content, b"True")
        self.assertEqual(NotificationStaff.objects.count(), 1)

        # Test send_student_notification POST
        data = {"id": self.student.admin.id, "message": "Test notification"}
        response = self.client.post(reverse("send_student_notification"), data=data)
        self.assertEqual(response.content, b"True")
        self.assertEqual(NotificationStudent.objects.count(), 1)

    def test_delete_views(self):
        # Test delete_staff
        self.assertEqual(CustomUser.objects.filter(staff__id=self.staff.id).count(), 1)
        response = self.client.get(reverse("delete_staff", args=[self.staff.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CustomUser.objects.filter(staff__id=self.staff.id).count(), 0)

        # Test delete_student
        self.assertEqual(
            CustomUser.objects.filter(student__id=self.student.id).count(), 1
        )
        response = self.client.get(reverse("delete_student", args=[self.student.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            CustomUser.objects.filter(student__id=self.student.id).count(), 0
        )

        # Test delete_course
        self.assertEqual(Course.objects.filter(id=self.course.id).count(), 1)
        response = self.client.get(reverse("delete_course", args=[self.course.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Course.objects.filter(id=self.course.id).count(), 0)

        # TODO: Fix. doesn't work
        # Test delete_subject.
        # self.assertEqual(Subject.objects.filter(id=self.subject.id).count(), 1)
        # response = self.client.get(reverse("delete_subject", args=[self.subject.id]))
        # self.assertEqual(Subject.objects.filter(id=self.subject.id).count(), 0)

        # Test delete_session
        self.assertEqual(Session.objects.filter(id=self.session.id).count(), 1)
        response = self.client.get(reverse("delete_session", args=[self.session.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Session.objects.filter(id=self.session.id).count(), 0)

    def test_edit_student(self):
        # Test GET request
        response = self.client.get(reverse("edit_student", args=[self.student.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_student_template.html")

        # Test POST request with valid data and password doesn't exist
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

        # Test POST request with valid data and password exists
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

        # Test POST request with invalid email
        data_with_password["email"] = "invalidemail"
        response = self.client.post(
            reverse("edit_student", args=[self.student.id]), data=data_with_password
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_student_template.html")
        self.assertFormError(response, "form", "email", "Enter a valid email address.")

    def test_edit_course(self):
        # Test GET request
        response = self.client.get(reverse("edit_course", args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_course_template.html")

        # Test POST request with valid data
        data = {"name": "Updated Course"}
        response = self.client.post(
            reverse("edit_course", args=[self.course.id]), data=data, follow=True
        )
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Updated Course")

        # Test POST request with invalid data
        data = {"name": ""}
        response = self.client.post(
            reverse("edit_course", args=[self.course.id]), data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_course_template.html")
        self.assertFormError(response, "form", "name", "This field is required.")

    def test_edit_subject(self):
        # Test GET request
        response = self.client.get(reverse("edit_subject", args=[self.subject.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_subject_template.html")

        # Test POST request with valid data
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

        # Test POST request with invalid data
        data = {"name": "", "course": self.course.id, "staff": self.staff.id}
        response = self.client.post(
            reverse("edit_subject", args=[self.subject.id]), data=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_subject_template.html")
        self.assertFormError(response, "form", "name", "This field is required.")

    def test_edit_session(self):
        # Test GET request
        response = self.client.get(reverse("edit_session", args=[self.session.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_session_template.html")

        # Test POST request with valid data
        data = {"start_year": "2023-01-01", "end_year": "2024-12-31"}
        response = self.client.post(
            reverse("edit_session", args=[self.session.id]), data=data
        )
        self.assertEqual(response.status_code, 302)
        self.session.refresh_from_db()
        self.assertEqual(str(self.session.start_year), "2023-01-01")
        self.assertEqual(str(self.session.end_year), "2024-12-31")

        # Test POST request with invalid data
        data = {"start_year": "2024-01-01", "end_year": "2023-12-31"}
        response = self.client.post(
            reverse("edit_session", args=[self.session.id]), data=data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/edit_session_template.html")
        self.assertFormError(
            response, "form", None, "Start date should be before end date."
        )

    def test_add_student(self):
        # Test GET request
        response = self.client.get(reverse("add_student"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_student_template.html")

        # Test POST request with valid data
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
        self.assertEqual(
            CustomUser.objects.filter(email="newstudent@test.com").count(), 1
        )

        # Test POST request with invalid data
        data["email"] = "invalidemailformat"
        response = self.client.post(reverse("add_student"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            CustomUser.objects.filter(email="invalidemailformat").count(), 0
        )

    def test_add_subject(self):
        # Test GET request
        response = self.client.get(reverse("add_subject"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_subject_template.html")

        # Test POST request with valid data
        data = {
            "name": "New Subject",
            "course": self.course.id,
            "staff": self.staff.id,
        }
        response = self.client.post(reverse("add_subject"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Subject.objects.filter(name="New Subject").count(), 1)

        # Test POST request with invalid data
        data = {"name": "", "course": self.course.id, "staff": self.staff.id}
        response = self.client.post(reverse("add_subject"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_subject_template.html")

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

    def test_add_session(self):
        # Test GET request
        response = self.client.get(reverse("add_session"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_session_template.html")

        # Test POST request with valid data
        data = {"start_year": "2024-01-01", "end_year": "2025-12-31"}
        response = self.client.post(reverse("add_session"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Session.objects.filter(
                start_year="2024-01-01", end_year="2025-12-31"
            ).count(),
            1,
        )

        # Test POST request with invalid data
        data = {"start_year": "2025-01-01", "end_year": "2024-12-31"}
        response = self.client.post(reverse("add_session"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/add_session_template.html")

    def test_manage_session(self):
        response = self.client.get(reverse("manage_session"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/manage_session.html")

    def test_staff_feedback_message(self):
        # Test GET request for viewing staff feedback
        response = self.client.get(reverse("staff_feedback_message"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/staff_feedback_template.html")

        # Test POST request for replying to staff feedback
        feedback = FeedbackStaff.objects.create(
            staff=self.staff, feedback="Staff test feedback"
        )
        data = {"id": feedback.id, "reply": "Reply to staff feedback"}
        response = self.client.post(reverse("staff_feedback_message"), data=data)
        self.assertEqual(response.content, b"True")
        feedback.refresh_from_db()
        self.assertEqual(feedback.reply, "Reply to staff feedback")

    def test_view_staff_leave(self):
        # Test GET request for viewing staff leave applications
        response = self.client.get(reverse("view_staff_leave"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hod_template/staff_leave_view.html")

        # Test POST request to approve staff leave
        leave = LeaveReportStaff.objects.create(
            staff=self.staff, date="2023-07-01", message="Test leave for staff"
        )
        data = {"id": leave.id, "status": "1"}
        response = self.client.post(reverse("view_staff_leave"), data=data)
        self.assertEqual(response.content, b"True")
        leave.refresh_from_db()
        self.assertEqual(leave.status, 1)

        # Test POST request to disapprove staff leave
        data = {"id": leave.id, "status": "2"}
        response = self.client.post(reverse("view_staff_leave"), data=data)
        self.assertEqual(response.content, b"True")
        leave.refresh_from_db()
        self.assertEqual(leave.status, -1)

    def test_get_admin_attendance(self):
        # Setting up attendance records
        attendance = Attendance.objects.create(
            subject=self.subject, session=self.session, date="2023-07-15"
        )
        AttendanceReport.objects.create(
            attendance=attendance, student=self.student, status=True
        )

        # Test POST request to fetch attendance data
        data = {
            "subject": self.subject.id,
            "session": self.session.id,
            "attendance_date_id": attendance.id,
        }
        response = self.client.post(reverse("get_admin_attendance"), data=data)
        response_list = json.loads(response.json())
        self.assertIsInstance(response_list, list)
        self.assertEqual(len(response_list), 1)
        self.assertEqual(response_list[0]["status"], "True")
        self.assertEqual(response_list[0]["name"], str(self.student))

    def test_delete_subject(self):
        # Test GET request to delete a subject
        response = self.client.get(reverse("delete_subject", args=[self.subject.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Subject.objects.filter(id=self.subject.id).count(), 0)
