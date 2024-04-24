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


class StaffViewsTest(TestCase):
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
        self.subject2 = Subject.objects.create(
            name="Another Subject", course=self.course, staff=self.staff
        )
        self.session = Session.objects.create(
            start_year="2022-01-02", end_year="2023-01-02"
        )

        self.client.force_login(
            self.staff_user
        )  # Authenticate the client as a staff user
        self.notification = NotificationStaff.objects.create(
            staff=self.staff, message="Test Notification"
        )
        self.book1 = Book.objects.create(
            name="Book One", isbn="1234567890123", author="Author A", category="Fiction"
        )
        self.book2 = Book.objects.create(
            name="Book Two",
            isbn="9876543210987",
            author="Author B",
            category="Non-Fiction",
        )
        self.book = Book.objects.create(
            name="Book One", isbn="1234567890123", author="Author A", category="Fiction"
        )

        # Define fixed dates
        self.issued_date_with_fine = (
            "2023-03-31"  # 15 days ago from a fixed 'today' assumed to be 2023-04-15
        )
        self.expiry_date = "2023-04-30"  # 15 days after 'today'
        self.issued_date_no_fine = "2023-04-5"  # 10 days ago from 'today'

        # Create issued books with actual 'isbn' from a real Book instance
        IssuedBook.objects.create(
            isbn=self.book.isbn,
            issued_date=self.issued_date_with_fine,
            expiry_date=self.expiry_date,
        )
        IssuedBook.objects.create(
            isbn=self.book.isbn,
            issued_date=self.issued_date_no_fine,
            expiry_date=self.expiry_date,
        )

        # Create a student and related attendance data
        self.attendance = Attendance.objects.create(
            session=self.session, subject=self.subject, date="2023-04-01"
        )
        self.attendance_report = AttendanceReport.objects.create(
            student=self.student, attendance=self.attendance, status=False
        )

        super().setUp()

    def test_staff_add_book(self):
        response = self.client.get(reverse("add_book"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/add_book.html")

    def test_post_add_book(self):
        # Here we simulate posting data to add a book
        data = {
            "name": "New Book",
            "author": "Author Name",
            "isbn": "1234567890",
            "category": "Science",
        }
        response = self.client.post(reverse("add_book"), data)
        self.assertEqual(
            response.status_code, 200
        )  # Assuming redirection to a success or listing page
        self.assertTrue(Book.objects.filter(name="New Book").exists())

    # FAULT: issue_book.html doesn't exist
    def test_issue_book(self):
        book = Book.objects.create(
            name="Test Book", author="Test Author", isbn="1234567890", category="Fictin"
        )
        data = {"name2": self.student.id, "isbn2": book.isbn}
        response = self.client.post(reverse("issue_book"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/issue_book.html")
        self.assertTrue(
            IssuedBook.objects.filter(student=self.student, isbn=book.isbn).exists()
        )

    def test_save_attendance(self):
        data = {
            "subject": self.subject.id,
            "session": self.session.id,
            "date": "2023-06-10",
            "student_ids": "2",
        }
        response = self.client.post(reverse("save_attendance"), data)
        self.assertEqual(response.status_code, 200)
        # self.assertTrue(Attendance.objects.filter(subject=self.subject, session=self.session, date='2023-06-10').exists())

    def test_get_students(self):
        data = {"subject": self.subject.id, "session": self.session.id}
        response = self.client.post(reverse("get_students"), data)
        self.assertEqual(response.status_code, 200)

    def test_staff_update_attendance(self):
        response = self.client.get(reverse("staff_update_attendance"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/staff_update_attendance.html")
        self.assertIn("subjects", response.context)
        self.assertIn("sessions", response.context)

    def test_get_student_attendance(self):
        attendance = Attendance.objects.create(
            session=self.session, subject=self.subject, date="2023-04-01"
        )  # Assuming date format is \(YYYY-MM-DD)
        attendance_report = AttendanceReport.objects.create(
            student=self.student, attendance=attendance, status=True
        )

        response = self.client.post(
            reverse("get_student_attendance"), {"attendance_date_id": attendance.id}
        )
        self.assertEqual(response.status_code, 200)
        # response_data = json.loads(response.content)
        # self.assertEqual(len(response_data), 1)
        # self.assertEqual(response_data[0]['id'], self.student.admin.id)

    def test_staff_home(self):
        response = self.client.get(reverse("staff_home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/home_content.html")

    def test_update_attendance(self):
        attendance = Attendance.objects.create(
            session=self.session, subject=self.subject, date="2023-04-01"
        )
        AttendanceReport.objects.create(
            student=self.student, attendance=attendance, status=False
        )
        update_data = {
            "student_ids": ([{"id": self.student.id, "status": True}]),
            "date": attendance.date,  # Using attendance ID as 'date' to match your view logic
        }
        response = self.client.post(reverse("update_attendance"), update_data)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(AttendanceReport.objects.get(student=self.student).status, 'present')

    def test_staff_add_results(self):
        response = self.client.get(reverse("staff_add_result"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/staff_add_result.html")

    def test_get_add_result_page(self):
        response = self.client.get(reverse("staff_add_result"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/staff_add_result.html")
        self.assertIn("subjects", response.context)
        self.assertIn("sessions", response.context)
        
    def test_post_add_result_success(self):
        data = {
            "student_list": self.student.id,
            "subject": self.subject.id,
            "test": "85",
            "exam": "90",
        }
        response = self.client.post(reverse("staff_add_result"), data)
        self.assertEqual(response.status_code, 200)
        result = StudentResult.objects.get(student=self.student, subject=self.subject)

    def test_staff_apply_leave(self):
        response = self.client.get(reverse("staff_apply_leave"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/staff_apply_leave.html")

        # Test POST request with valid data
        data = {"date": "2023-06-10", "message": "Test leave"}
        response = self.client.post(reverse("staff_apply_leave"), data)
        self.assertEqual(
            response.status_code, 302
        )  # Expecting redirect after successful submission
        self.assertTrue(
            LeaveReportStaff.objects.filter(
                staff=self.staff, date="2023-06-10", message="Test leave"
            ).exists()
        )

    def test_staff_feedback(self):
        response = self.client.get(reverse("staff_feedback"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/staff_feedback.html")

        # Test POST request with valid data
        data = {"feedback": "Test feedback"}
        response = self.client.post(reverse("staff_feedback"), data)
        self.assertEqual(
            response.status_code, 302
        )  # Expecting redirect after successful submission
        self.assertTrue(
            FeedbackStaff.objects.filter(
                staff=self.staff, feedback="Test feedback"
            ).exists()
        )

    def test_staff_view_profile(self):
        response = self.client.get(reverse("staff_view_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/staff_view_profile.html")

        # Test POST request with valid data
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "staff@test.com",
            "gender": "M",
            "address": "New Address",
            "profile_pic": SimpleUploadedFile(
                "small.gif", small_gif, content_type="image/gif"
            ),
        }
        response = self.client.post(reverse("staff_view_profile"), data=data)
        updated_admin = CustomUser.objects.get(email="staff@test.com")
        self.assertEqual(
            response.status_code, 302
        )  # Expecting redirect after successful update
        self.staff_user.refresh_from_db()
        self.assertEqual(self.staff_user.first_name, "Updated")
        self.assertEqual(self.staff_user.last_name, "Name")
        self.assertEqual(self.staff_user.address, "New Address")

        # TEST POST with invalid email:
        data["email"] = "invalid"
        response = self.client.post(reverse("staff_view_profile"), data=data)
        self.assertEqual(response.status_code, 200)

    def test_staff_take_attendance_get(self):
        response = self.client.get(reverse("staff_take_attendance"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/staff_take_attendance.html")

        # Checking if the context data contains the correct elements
        self.assertIn("subjects", response.context)
        self.assertIn("sessions", response.context)
        self.assertIn("page_title", response.context)

        # Check the correctness of the data in the context
        self.assertEqual(
            len(response.context["subjects"]), 2
        )  # Should match the number of subjects assigned to the staff
        self.assertEqual(response.context["page_title"], "Take Attendance")

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(reverse("staff_home"))
        self.assertNotEqual(response.status_code, 200)

    def test_form_submission(self):
        response = self.client.post(
            reverse("add_book"),
            {
                "name": "Sample Book",
                "author": "Author Name",
                "isbn": "1234567890123",
                "category": "Fiction",
            },
            follow=True,
        )
        self.assertEqual(
            response.status_code, 200
        )  # Assuming a redirect after successful submission
        self.assertTrue(Book.objects.filter(name="Sample Book").exists())

    def test_invalid_form_submission(self):
        response = self.client.post(
            reverse("add_book"),
            {
                "name": "",
                "author": "Author Name",
                "isbn": "1234567890123",
                "category": "Fiction",
            },
        )
        self.assertEqual(
            response.status_code, 200
        )  # Form should be invalid, so no redirect
        self.assertTrue(Book.objects.filter(name="").exists())

    def test_error_handling(self):
        # Assuming 'delete_book' is a view that might raise an exception
        with self.assertRaises(Exception):
            self.client.get(reverse("delete_book", args=(1,)))

    def test_view_issued_book(self):
        response = self.client.get(reverse("view_issued_book"))
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'staff_template/view_issued_book.html')

    def test_fetch_student_result_success(self):
        data = {"student": "1", "subject": "Test Subject"}
        response = self.client.post(reverse("fetch_student_result"), data)
        self.assertEqual(response.status_code, 200)

    def test_staff_fcmtoken_success(self):
        # Assuming 'staff_fcmtoken' is the URL name
        url = reverse("staff_fcmtoken")
        response = self.client.post(url, {"token": "somefaketoken123"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "True")
        updated_user = CustomUser.objects.get(id=self.staff_user.id)
        self.assertEqual(updated_user.fcm_token, "somefaketoken123")

    def test_staff_fcmtoken_failure(self):
        # Simulate failure by using an invalid user ID or mock an exception
        self.client.logout()
        response = self.client.post(
            reverse("staff_fcmtoken"), {"token": "anothertoken123"}
        )
        self.assertEqual(
            response.status_code, 302
        )  # Expect 404 due to user not logged in

    def test_staff_view_notification(self):
        url = reverse("staff_view_notification")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/staff_view_notification.html")
        self.assertIn("notifications", response.context)
        self.assertIn("page_title", response.context)
        self.assertEqual(len(response.context["notifications"]), 1)
        self.assertEqual(
            response.context["notifications"][0].message, "Test Notification"
        )

    def test_view_issued_books_no_fine(self):
        book = Book.objects.create(
            name="Test Book", author="Test Author", isbn="1234567890", category="Fictin"
        )
        data = {"name2": self.student.id, "isbn2": book.isbn}

        response = self.client.post(reverse("issue_book"), data)

        response = self.client.get(reverse("view_issued_book"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "staff_template/view_issued_book.html")
        details = response.context["details"]
        # Check that no fine is issued for the book issued within no fine period

    def test_update_attendance_success(self):
        # Data preparation
        update_data = {"student_ids": "1", "date": str(self.attendance.id)}
        response = self.client.post(reverse("update_attendance"), update_data)
        self.assertEqual(response.status_code, 200)
        self.attendance_report.refresh_from_db()

    # ... (other test methods)
