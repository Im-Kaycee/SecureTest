from django.contrib import admin
from .models import Student, Course, CourseRegistration, AttendanceRecord, Exam, ExamQuestion
from .forms import ExamQuestionForm
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'matric_no', 'created_at')
    search_fields = ('user__username', 'matric_no')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title')
    search_fields = ('code', 'title')

@admin.register(CourseRegistration)
class CourseRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'course')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'attendance_percentage')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'start_time', 'end_time')

from django.contrib import admin
from .models import ExamQuestion

class ExamQuestionAdmin(admin.ModelAdmin):
    form = ExamQuestionForm
    list_display = ['exam', 'question_text', 'correct_option']

admin.site.register(ExamQuestion, ExamQuestionAdmin)