from django import forms

class SubmissionForm(forms.Form):
    name = forms.CharField(max_length=100, label="Nombre del Alumno")
    student_id = forms.CharField(max_length=20, label="ID del Alumno")
    blog_url = forms.URLField(label="URL del Blog")
    pdf_file = forms.FileField(label="Archivo PDF de las Entradas")