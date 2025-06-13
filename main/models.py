

from django.db import models
from django.contrib.auth.models import User

# Optional: Replace with a custom User model later if needed

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matric_no = models.CharField(max_length=20, unique=True)
    fingerprint_credential = models.JSONField(null=True, blank=True)  # WebAuthn credential
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.matric_no


class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.title}"


class CourseRegistration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} registered for {self.course}"


class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    attendance_percentage = models.FloatField(default=0)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} - {self.course}: {self.attendance_percentage}%"

from django.utils.text import slugify
class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.course.code})"
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


from cryptography.fernet import Fernet
from django.conf import settings
import base64

class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions',default=None, null=True)
    encrypted_question_text = models.BinaryField(default=b'')
    encrypted_option_a = models.BinaryField(default=b'')
    encrypted_option_b = models.BinaryField(default=b'')
    encrypted_option_c = models.BinaryField(default=b'')
    encrypted_option_d = models.BinaryField(default=b'')
    encrypted_correct_option = models.BinaryField(default=b'')

    def _fernet(self):
        return Fernet(settings.FERNET_KEY)

    # Properties for transparent access
    @property
    def question_text(self):
        return self._fernet().decrypt(self.encrypted_question_text).decode()

    @question_text.setter
    def question_text(self, value):
        self.encrypted_question_text = self._fernet().encrypt(value.encode())

    @property
    def option_a(self):
        return self._fernet().decrypt(self.encrypted_option_a).decode()

    @option_a.setter
    def option_a(self, value):
        self.encrypted_option_a = self._fernet().encrypt(value.encode())

    @property
    def option_b(self):
        return self._fernet().decrypt(self.encrypted_option_b).decode()

    @option_b.setter
    def option_b(self, value):
        self.encrypted_option_b = self._fernet().encrypt(value.encode())

    @property
    def option_c(self):
        return self._fernet().decrypt(self.encrypted_option_c).decode()

    @option_c.setter
    def option_c(self, value):
        self.encrypted_option_c = self._fernet().encrypt(value.encode())

    @property
    def option_d(self):
        return self._fernet().decrypt(self.encrypted_option_d).decode()

    @option_d.setter
    def option_d(self, value):
        self.encrypted_option_d = self._fernet().encrypt(value.encode())

    @property
    def correct_option(self):
        return self._fernet().decrypt(self.encrypted_correct_option).decode()

    @correct_option.setter
    def correct_option(self, value):
        self.encrypted_correct_option = self._fernet().encrypt(value.encode())

    def __str__(self):
        return f"Q: {self.question_text[:30]}..."