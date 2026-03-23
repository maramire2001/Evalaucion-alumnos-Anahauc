from django.contrib import admin
from .models import Student, Submission, Grade

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'blog_url', 'submitted_at')
    list_filter = ('submitted_at',)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('submission', 'blog_score', 'entries_score', 'total_score', 'adjustments', 'final_score')
    list_editable = ('adjustments',)
    ordering = ('-final_score',)  # Sort from best to worst
