# 🚀 Despliegue en GitHub + Render - Guía Paso a Paso

## Fase 1: Crear Repositorio en GitHub

### Opción A: Desde GitHub Web UI (Recomendado)

1. **Ir a GitHub.com**
   - Inicia sesión en tu cuenta (o crea una si no tienes)

2. **Crear nuevo repositorio**
   - Click en "+" → "New repository"
   - Nombre: `evaluacion-maestria-anahuac` (o el que prefieras)
   - Descripción: "Full-stack Django app with Groq AI for evaluating student blogs"
   - **Seleccionar**: Public (para que Render pueda acceder)
   - NO inicializar con README, .gitignore, ni license (porque ya los tenemos)
   - Click "Create repository"

3. **Copiar el HTTPS URL**
   - Verás algo como: `https://github.com/TU_USUARIO/evaluacion-maestria-anahuac.git`
   - Cópialo

### Opción B: Desde Terminal (GitHub CLI)

```bash
# Si tienes GitHub CLI instalado
gh auth login  # Inicia sesión si no lo estás
gh repo create evaluacion-maestria-anahuac --public --source=. --remote=origin --push
```

---

## Fase 2: Hacer Push a GitHub (Desde Tu Mac)

### Ejecutar en terminal:

```bash
cd /Users/maramire2001/Desktop/Apps\ Mario/Evalaución\ Maestria\ Anahuac

# 1. Añadir origin remoto
git remote add origin https://github.com/TU_USUARIO/evaluacion-maestria-anahuac.git

# 2. Cambiar branch a main (si está en master)
git branch -M main

# 3. Hacer push (primera vez con -u)
git push -u origin main
```

### Verificar en GitHub
- Ve a tu repositorio en GitHub
- Deberías ver todos los archivos (26 archivos)
- Verifica que .env NO está (está en .gitignore)

---

## Fase 3: Desplegar en Render

### Paso 1: Crear Web Service en Render

1. **Ir a Render.com**
   - Inicia sesión o crea cuenta
   - Dashboard → "New +"

2. **Conectar GitHub**
   - Click en "Web Service"
   - Selecciona "Connect a repository"
   - Autoriza Render a acceder a tu GitHub
   - Busca y selecciona: `evaluacion-maestria-anahuac`

### Paso 2: Configurar Servicio Web

**Build Settings:**
- Name: `evaluacion-maestria-anahuac` (o tu_nombre)
- Environment: `Python 3`
- Build Command:
  ```
  pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --no-input
  ```
- Start Command:
  ```
  gunicorn evaluation.wsgi
  ```

**Environment Variables** (agregar las siguientes):
```
GROQ_API_KEY=your_groq_api_key_here
DEBUG=False
SECRET_KEY=tu_secret_key_muy_largo_aleatorio_aqui
ALLOWED_HOSTS=tu-app.onrender.com,www.tu-app.onrender.com
```

Para generar un buen SECRET_KEY:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Premium Features to Add (Opcional pero Recomendado):**
- PostgreSQL Database (mejor que SQLite)

### Paso 3: Deploy

- Click "Create Web Service"
- Render empezará a hacer deploy automáticamente
- Verás logs en vivo
- Espera a que termine (2-3 minutos)

### Paso 4: Verificar Deploy

1. **Ir a tu URL** (Render te da una URL: `https://evaluacion-maestria-anahuac.onrender.com`)

2. **Probar endpoints:**
   - Alumno form: `/submit/`
   - Admin: `/admin/` (usar credenciales que creaste)
   - Exportar: `/export/`

---

## 🔧 Configuration Update en settings.py

Si necesitas actualizar `evaluation/settings.py` para producción:

```python
# En evaluation/settings.py

DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Para PostgreSQL en Render:
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
```

---

## 📝 Workflow Futuro (Cambios y Actualizaciones)

Una vez que todo está en Render + GitHub:

### Cuando hagas cambios locales:

```bash
# 1. Hacer cambios en tu código local
# 2. Commitear
git add .
git commit -m "Descripción del cambio"

# 3. Hacer push a GitHub
git push origin main

# 4. Render detecta automáticamente y redeploya
#    (Sin que hagas nada extra - hace deploy automático)
```

---

## 🔄 Deploy Automático (Auto Deploy)

Render está configurado para **hacer deploy automático** cuando hagas push a `main`:

1. Commit + Push a GitHub
2. Render recibe webhook
3. Render baja el código
4. Corre los comandos de Build
5. Reinicia la app
6. Tu cambio está en vivo

⏱️ Tiempo: ~2-3 minutos

---

## 🗄️ Base de Datos Recomendada

### SQLite (Actual - Desarrollo)
- ✅ Fácil para desarrollo
- ❌ No ideal para producción con múltiples usuarios
- ❌ Render reinicia la app y pierde datos si no está conectada a volumen persistente

### PostgreSQL (Recomendada - Producción)
- ✅ Persistencia garantizada
- ✅ Múltiples usuarios simultáneos
- ✅ Backups automáticos

**Agregar PostgreSQL en Render:**
1. Dashboard de Render → "New +" → "PostgreSQL"
2. Conectar a tu Web Service
3. Render automáticamente inyecta `DATABASE_URL` como variable de entorno
4. Migrar: `python manage.py migrate`

---

## ✅ Checklist Final

- [ ] Repositorio creado en GitHub
- [ ] Código pusheado a GitHub (git push)
- [ ] Variables de entorno configuradas en Render
- [ ] Deploy completado en Render
- [ ] Endpoints funcionando:
  - [ ] `/submit/` - Formulario de alumno
  - [ ] `/admin/` - Panel de admin
  - [ ] `/export/` - Excel
- [ ] Crear superusuario en producción:
  ```bash
  # En tu máquina, conectar a la DB de Render y crear user:
  python manage.py createsuperuser --settings=evaluation.settings
  ```

---

## 🆘 Troubleshooting

### Error: "No Module" en Render
- Verifica que `requirements.txt` esté actualizado
- Commit + push nuevamente

### Error: "Database locked" (SQLite)
- Cambiar a PostgreSQL (recomendado)

### Error: Static files 404
- Render debe correr: `collectstatic` en Build Command (ya incluido)

### Error: Groq API Key
- Verificar que esté bien configurada en Render Environment Variables
- No debe tener espacios

---

## 📞 Próximos Pasos

1. **Crear repo en GitHub** (seguir instrucciones arriba)
2. **Hacer push**: `git push -u origin main`
3. **Crear Web Service en Render** (conectar a GitHub)
4. **Configurar variables de entorno**
5. **Deploy automático** 🚀

---

**Última actualización**: 23 de marzo de 2026
**Versión**: 1.0 - GitHub + Render Ready