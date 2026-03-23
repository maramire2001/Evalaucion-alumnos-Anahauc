# Evaluación de Blogs de Maestría en Métodos Cuantitativos

Esta aplicación web permite a los alumnos de maestría subir sus blogs y PDFs de entradas para evaluación automática basada en una rúbrica detallada con IA (Groq).

## Características

- **Subida de Trabajos**: Los alumnos pueden subir su nombre, ID, URL del blog y archivo PDF de las entradas.
- **Evaluación Automática con IA**: Scraping del blog para detectar entradas, cruce con PDF, y calificación automática usando Groq AI basada en rúbrica.
- **Panel de Administrador**: Vista de calificaciones ordenadas de mejor a peor, ajuste manual con justificaciones, trabajos archivados.
- **Exportación a Excel**: Genera un archivo Excel con calificaciones individuales y grupales.

## Rúbrica (Basada en Modelo Proporcionado - Con Evaluación IA)

La evaluación utiliza Groq AI (modelo Llama 3.1 8B) para análisis semántico profundo:

- **Cantidad y Regularidad de Entregas (35%)**: Groq evalúa si hay aproximadamente 16 entradas temáticas con coherencia y continuidad.
- **Calidad del Contenido (35%)**: Groq analiza profundidad analítica, redacción clara, apropiación conceptual de métodos cuantitativos, estructura académica.
- **Presentación y Diseño del Blog (10%)**: Groq valida cuidado visual, uso estratégico de imágenes, tablas, navegación intuitiva.
- **Protocolo de Investigación (20%)**: Groq revisa claridad metodológica, formulación rigurosa de variables, estructura académica en el PDF.

**Cálculo Final**: (Cantidad × 0.35) + (Calidad × 0.35) + (Presentación × 0.10) + (Protocolo × 0.20)

**Ventajas de la IA**:
- Evaluación semántica (no solo keywords).
- Justificaciones automáticas para cada criterio.
- Consistencia en la evaluación.
- Análisis profundo de rigor metodológico.

## Instalación

1. Instalar dependencias: `pip install -r requirements.txt`
2. Crear archivo `.env` con: `GROQ_API_KEY=tu_api_key_aqui`
3. Ejecutar migraciones: `python manage.py migrate`
4. Crear superusuario: `python manage.py createsuperuser`
5. Ejecutar servidor: `python manage.py runserver`

## Uso

- **Alumnos**: Ir a `/submit/` para subir trabajos.
- **Administrador**: Ir a `/admin/` para ver calificaciones (ordenadas de mejor a peor), ajustar, revisar trabajos, y `/export/` para descargar Excel.

## Despliegue en Render

1. Configurar como web service con comando: `python manage.py runserver 0.0.0.0:$PORT`
2. Agregar variable de entorno: `GROQ_API_KEY=tu_api_key_aqui`
3. Configurar PostgreSQL o SQLite según necesidad.

## Arquitectura

- **Backend**: Django 4.2 con SQLite/PostgreSQL
- **Evaluación**: Groq AI (Llama 3.1 8B) para análisis automático
- **Scraping**: BeautifulSoup + Requests
- **PDFs**: pypdf para extracción de texto
- **Excel**: openpyxl para generación de reportes
- **Frontend**: HTML/Django templates (simple)

## Variables de Entorno

```env
GROQ_API_KEY=your_groq_api_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```