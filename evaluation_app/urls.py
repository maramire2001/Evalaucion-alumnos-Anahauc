from django.urls import path
from . import views

urlpatterns = [
    path('', views.submit_assignment, name='home'),
    path('submit/', views.submit_assignment, name='submit'),
    path('export/', views.export_grades, name='export'),

    # Panel del Profesor
    path('profesor/', views.profesor_dashboard, name='profesor_dashboard'),
    path('profesor/descargar/<int:submission_id>/', views.download_pdf, name='download_pdf'),
    path('profesor/descargar-todos/', views.download_all_pdfs, name='download_all_pdfs'),
    path('profesor/portada/<int:submission_id>/', views.pdf_portada, name='pdf_portada'),
    path('profesor/recalcular/<int:submission_id>/', views.recalcular_calificacion, name='recalcular'),

    # Reporte de subidas
    path('profesor/subidas/', views.reporte_subidas, name='reporte_subidas'),
    path('profesor/subidas/excel/', views.export_subidas_excel, name='export_subidas_excel'),
]
