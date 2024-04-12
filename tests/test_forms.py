from django.test import TestCase
from main_app.forms import (
    CustomUserForm, StudentForm, AdminForm, StaffForm, CourseForm, SubjectForm, 
    SessionForm, LeaveReportStaffForm, FeedbackStaffForm, LeaveReportStudentForm,
    FeedbackStudentForm, StudentEditForm, StaffEditForm, EditResultForm, IssueBookForm
)
from main_app.models import CustomUser, Student, Course, Session, Book

class CustomUserFormTest(TestCase):
    def test_clean_email_for_existing_email(self):
        # Create a user with email
        CustomUser.objects.create(email='test@example.com')
        
        form = CustomUserForm(data={
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'gender': 'M',
            'password': 'password123',
        })
        
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ["The given email is already registered"])

    def test_clean_email_for_new_email(self):
        form = CustomUserForm(data={
            'email': 'newuser@example.com',
            'first_name': 'John',  
            'last_name': 'Doe',
            'gender': 'M',
            'password': 'password123',
        })
        
        self.assertTrue(form.is_valid())

class StudentFormTest(TestCase):
    def test_student_form_fields(self):
        form = StudentForm()
        self.assertEqual(list(form.fields.keys()), [
            'first_name', 'last_name', 'email', 'gender', 'password', 
            'profile_pic', 'address', 'course', 'session'
        ])

class CourseFormTest(TestCase):  
    def test_course_form_fields(self):
        form = CourseForm()
        self.assertEqual(list(form.fields.keys()), ['name'])

class SessionFormTest(TestCase):
    def test_session_form_fields(self):  
        form = SessionForm()
        self.assertEqual(list(form.fields.keys()), ['start_year', 'end_year'])

class IssueBookFormTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(isbn='1234567890')
        self.student = Student.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            gender='M'
        )

    def test_issue_book_form_fields(self):
        form = IssueBookForm()  
        self.assertEqual(list(form.fields.keys()), ['isbn2', 'name2'])

    def test_issue_book_form_initial_data(self):
        form = IssueBookForm(initial={
            'isbn2': self.book,
            'name2': self.student    
        })

        self.assertEqual(form.initial['isbn2'], self.book)
        self.assertEqual(form.initial['name2'], self.student)