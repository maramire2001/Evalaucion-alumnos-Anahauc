from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.student_id})"

class Submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    blog_url = models.URLField()
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    # PDF guardado directo en PostgreSQL — no se pierde con reinicios
    pdf_data = models.BinaryField(blank=True, null=True)
    pdf_filename = models.CharField(max_length=255, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.student} on {self.submitted_at}"

class Grade(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE)
    blog_score = models.FloatField(default=0)
    entries_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)
    adjustments = models.TextField(blank=True)
    final_score = models.FloatField(default=0)

    def __str__(self):
        return f"Grade for {self.submission}: {self.final_score}"
