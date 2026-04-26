from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime,timedelta




class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)


class CustomUser(AbstractUser):
    # String keys so CharField comparisons are always consistent.
    # Integer keys (the original) caused `1 == '1'` → False in Python 3,
    # which broke login redirects and get_user_type_display().
    USER_TYPE = (('1', "HOD"), ('2', "Staff"), ('3', "Student"))
    GENDER = [("M", "Male"), ("F", "Female")]

    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default='1', choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField()
    address = models.TextField()
    fcm_token = models.TextField(default="")  # For firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return  self.first_name + " " + self.last_name


class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)



class Course(models.Model):
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.PositiveIntegerField()
    category = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name) + " ["+str(self.isbn)+']'


class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name

class Library(models.Model):
    student = models.ForeignKey(Student,  on_delete=models.CASCADE, null=True, blank=False)
    book = models.ForeignKey(Book,  on_delete=models.CASCADE, null=True, blank=False)
    def __str__(self):
        return str(self.student)

def expiry():
    return datetime.today() + timedelta(days=14)
class IssuedBook(models.Model):
    student_id = models.CharField(max_length=100, blank=True)
    isbn = models.PositiveIntegerField()
    issued_date = models.DateField(auto_now=True)
    expiry_date = models.DateField(default=expiry)



class Staff(models.Model):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.admin.first_name + " " +  self.admin.last_name


class Subject(models.Model):
    name = models.CharField(max_length=120)
    staff = models.ForeignKey(Staff,on_delete=models.CASCADE,)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        group_name = self.group.name if self.group else "—"
        return f"{group_name} · {self.date}"


class AttendanceReport(models.Model):
    ABSENT = 0
    PRESENT = 1
    LATE = 2
    STATUS_CHOICES = ((ABSENT, 'Absent'), (PRESENT, 'Present'), (LATE, 'Late'))

    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.SmallIntegerField(default=ABSENT, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'group')


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return
    user_type = str(instance.user_type)
    if user_type == '1':
        Admin.objects.get_or_create(admin=instance)
    elif user_type == '2':
        Staff.objects.get_or_create(admin=instance)
    elif user_type == '3':
        Student.objects.get_or_create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    user_type = str(instance.user_type)
    if user_type == '1':
        Admin.objects.get_or_create(admin=instance)
    elif user_type == '2':
        Staff.objects.get_or_create(admin=instance)
    elif user_type == '3':
        Student.objects.get_or_create(admin=instance)


class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Branches"


class Group(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    schedule = models.CharField(max_length=200, blank=True, default="",
                                help_text="e.g. Mon/Wed 10:00–12:00")
    capacity = models.PositiveIntegerField(default=20)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    enrolled_on = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'group')

    def __str__(self):
        return f"{self.student} → {self.group}"


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField()
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/', null=True, blank=True)
    note = models.TextField(blank=True, default="")
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student} → {self.assignment}"


class ResultFile(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to='results/')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    uploaded_by = models.ForeignKey(Staff, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    @property
    def filename(self):
        import os
        return os.path.basename(self.file.name) if self.file else ''
