from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .forms import SubmissionForm
from .models import Student, Submission, Grade
from .grading import grade_submission
import openpyxl

def submit_assignment(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            student_id = form.cleaned_data['student_id']
            blog_url = form.cleaned_data['blog_url']
            pdf_file = form.cleaned_data['pdf_file']

            student, created = Student.objects.get_or_create(
                student_id=student_id,
                defaults={'name': name}
            )
            if not created and student.name != name:
                student.name = name
                student.save()

            submission = Submission.objects.create(
                student=student,
                blog_url=blog_url,
                pdf_file=pdf_file
            )

            # Grade automatically
            grade = grade_submission(submission)
            grade.save()

            messages.success(request, 'Entrega enviada y calificada exitosamente.')
            return redirect('submit')
    else:
        form = SubmissionForm()
    return render(request, 'submit.html', {'form': form})

def export_grades(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Calificaciones"
    ws.append(['Alumno', 'ID', 'Blog Score', 'Entries Score', 'Total', 'Ajustes', 'Final'])
    for grade in Grade.objects.select_related('submission__student').order_by('-final_score'):
        ws.append([
            grade.submission.student.name,
            grade.submission.student.student_id,
            grade.blog_score,
            grade.entries_score,
            grade.total_score,
            grade.adjustments,
            grade.final_score
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=calificaciones.xlsx'
    wb.save(response)
    return response
