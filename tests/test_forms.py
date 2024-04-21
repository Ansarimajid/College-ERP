from django.test import TestCase
from main_app.forms import (
    CustomUserForm,
    StudentForm,
    AdminForm,
    StaffForm,
    CourseForm,
    SubjectForm,
    SessionForm,
    LeaveReportStaffForm,
    FeedbackStaffForm,
    LeaveReportStudentForm,
    FeedbackStudentForm,
    StudentEditForm,
    StaffEditForm,
    EditResultForm,
    IssueBookForm,
    FormSettings,
)
from main_app.models import *
from main_app.forms import *
from django.db import models

from django.test import TestCase, SimpleTestCase


class CustomUserFormTestCase(TestCase):
    def test_email_required(self):
        form = CustomUserForm(data={"email": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_gender_choices(self):
        form = CustomUserForm()
        gender_field = form.fields["gender"]
        self.assertEqual(gender_field.choices, [("M", "Male"), ("F", "Female")])

    def test_profile_pic_field(self):
        form = CustomUserForm()
        self.assertIsInstance(form.fields["profile_pic"], forms.ImageField)

    def test_password_widget(self):
        form = CustomUserForm()
        self.assertIsInstance(form.fields["password"].widget, forms.PasswordInput)

    def test_clean_email_insert(self):
        CustomUser.objects.create(email="test@example.com")
        form = CustomUserForm(data={"email": "test@example.com"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_clean_email_update(self):
        user = CustomUser.objects.create(email="test@example.com")
        form = CustomUserForm(instance=user, data={"email": "updated@example.com"})
        self.assertTrue(form.is_valid())


class StudentFormTestCase(TestCase):
    def test_meta_model(self):
        self.assertEqual(StudentForm.Meta.model, Student)

    def test_meta_fields(self):
        expected_fields = CustomUserForm.Meta.fields + ["course", "session"]
        self.assertEqual(StudentForm.Meta.fields, expected_fields)


class AdminFormTestCase(TestCase):
    def test_meta_model(self):
        self.assertEqual(AdminForm.Meta.model, Admin)

    def test_meta_fields(self):
        self.assertEqual(AdminForm.Meta.fields, CustomUserForm.Meta.fields)


class StaffFormTestCase(TestCase):
    def test_meta_model(self):
        self.assertEqual(StaffForm.Meta.model, Staff)

    def test_meta_fields(self):
        expected_fields = CustomUserForm.Meta.fields + ["course"]
        self.assertEqual(StaffForm.Meta.fields, expected_fields)


class CourseFormTestCase(TestCase):
    def test_meta_fields(self):
        self.assertEqual(CourseForm.Meta.fields, ["name"])

    def test_meta_model(self):
        self.assertEqual(CourseForm.Meta.model, Course)


class SubjectFormTestCase(TestCase):
    def test_meta_model(self):
        self.assertEqual(SubjectForm.Meta.model, Subject)

    def test_meta_fields(self):
        self.assertEqual(SubjectForm.Meta.fields, ["name", "staff", "course"])


class SessionFormTestCase(TestCase):
    def test_meta_model(self):
        self.assertEqual(SessionForm.Meta.model, Session)

    def test_meta_fields(self):
        self.assertEqual(SessionForm.Meta.fields, "__all__")

    def test_widgets(self):
        form = SessionForm()
        self.assertIsInstance(form.fields["start_year"].widget, DateInput)
        self.assertIsInstance(form.fields["end_year"].widget, DateInput)


class LeaveReportStaffFormTestCase(TestCase):
    def test_meta_model(self):
        self.assertEqual(LeaveReportStaffForm.Meta.model, LeaveReportStaff)

    def test_meta_fields(self):
        self.assertEqual(LeaveReportStaffForm.Meta.fields, ["date", "message"])

    def test_widgets(self):
        form = LeaveReportStaffForm()
        self.assertIsInstance(form.fields["date"].widget, DateInput)


class FeedbackStaffFormTestCase(TestCase):
    def test_meta_model(self):
        self.assertEqual(FeedbackStaffForm.Meta.model, FeedbackStaff)

    def test_meta_fields(self):
        self.assertEqual(FeedbackStaffForm.Meta.fields, ["feedback"])


class LeaveReportStudentFormTestCase(TestCase):
    def test_meta_model(self):
        self.assertEqual(LeaveReportStudentForm.Meta.model, LeaveReportStudent)

    def test_meta_fields(self):
        self.assertEqual(LeaveReportStudentForm.Meta.fields, ["date", "message"])

    def test_widgets(self):
        form = LeaveReportStudentForm()
        self.assertIsInstance(form.fields["date"].widget, DateInput)


class FeedbackStudentFormTestCase(TestCase):
    def test_meta_model(self):
        self.assertEqual(FeedbackStudentForm.Meta.model, FeedbackStudent)

    def test_meta_fields(self):
        self.assertEqual(FeedbackStudentForm.Meta.fields, ["feedback"])


class StudentEditFormTestCase(TestCase):
    def test_meta_model(self):
        self.assertEqual(StudentEditForm.Meta.model, Student)

    def test_meta_fields(self):
        self.assertEqual(StudentEditForm.Meta.fields, CustomUserForm.Meta.fields)


class StaffEditFormTestCase(TestCase):
    def test_meta_model(self):
        self.assertEqual(StaffEditForm.Meta.model, Staff)

    def test_meta_fields(self):
        self.assertEqual(StaffEditForm.Meta.fields, CustomUserForm.Meta.fields)


class EditResultFormTestCase(TestCase):
    def test_meta_model(self):
        self.assertEqual(EditResultForm.Meta.model, StudentResult)

    def test_meta_fields(self):
        self.assertEqual(
            EditResultForm.Meta.fields,
            ["session_year", "subject", "student", "test", "exam"],
        )

    def test_session_list(self):
        session = Session.objects.create(start_year="2023-01-01", end_year="2023-12-31")
        form = EditResultForm()
        self.assertQuerysetEqual(
            form.fields["session_year"].queryset, [session], transform=lambda x: x
        )


class IssueBookFormTestCase(TestCase):
    def test_form_fields(self):
        form = IssueBookForm()
        self.assertIsInstance(form.fields["isbn2"], forms.ModelChoiceField)
        self.assertIsInstance(form.fields["name2"], forms.ModelChoiceField)

    def test_form_widgets(self):
        form = IssueBookForm()
        self.assertIn("form-control", form.fields["isbn2"].widget.attrs["class"])
        self.assertIn("form-control", form.fields["name2"].widget.attrs["class"])
