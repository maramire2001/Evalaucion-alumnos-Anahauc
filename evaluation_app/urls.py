from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_assignment, name='submit'),
    path('export/', views.export_grades, name='export'),
]