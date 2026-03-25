"""
Ejecutar en el shell de Render (o localmente) para crear el superusuario del profesor:
    python manage.py shell < crear_superusuario.py

O directo desde Render Dashboard > Shell:
    python manage.py createsuperuser
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evaluation.settings')
django.setup()

from django.contrib.auth.models import User

USERNAME = 'profesor'
PASSWORD = 'AnAhuac2026!'    # <-- cambia esto por una contraseña segura
EMAIL = 'marioantonioramirezbarajas@gmail.com'

if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print(f"✅ Superusuario '{USERNAME}' creado con contraseña '{PASSWORD}'")
    print(f"   Accede en: /admin/  con usuario: {USERNAME}")
else:
    # Si ya existe, actualizar contraseña
    u = User.objects.get(username=USERNAME)
    u.set_password(PASSWORD)
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print(f"✅ Contraseña del usuario '{USERNAME}' actualizada.")
