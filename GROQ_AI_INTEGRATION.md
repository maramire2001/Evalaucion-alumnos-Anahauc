# Evaluación con Groq AI - Documentación Técnica

## ¿Cómo Funciona la IA en la Evaluación?

La aplicación utiliza **Groq AI** (modelo Llama 3.1 8B) para evaluar automáticamente los blogs y PDFs de los alumnos. En lugar de usar heurísticas simples (búsqueda de keywords), Groq realiza un análisis semántico profundo basado en la rúbrica específica de métodos cuantitativos.

### Flujo de Evaluación

1. **Alumno sube trabajos**
   - Link del blog
   - Archivo PDF de entradas

2. **Scraping y extracción**
   ```
   Blog URL → BeautifulSoup → Texto + Entradas detectadas
   PDF → pypdf → Texto completo
   ```

3. **Envío a Groq AI**
   ```python
   prompt = f"""Evalúa según rúbrica:
   - Cantidad y Regularidad (35%)
   - Calidad (35%)
   - Presentación (10%)
   - Protocolo (20%)
   
   Contenido del blog: {blog_text[:3000]}
   Contenido del PDF: {pdf_text[:3000]}
   
   Responde en JSON con scores y justificaciones."""
   ```

4. **Groq retorna JSON con scores (0-10) y justificaciones**
   ```json
   {
     "cantidad_score": 8,
     "calidad_score": 9,
     "presentacion_score": 7,
     "protocolo_score": 8,
     "justificaciones": {
       "cantidad": "16 entradas bien estructuradas",
       "calidad": "Profundidad analítica excepcional",
       ...
     }
   }
   ```

5. **Cálculo de calificación final**
   ```
   Final = (8 × 0.35) + (9 × 0.35) + (7 × 0.10) + (8 × 0.20) = 8.3
   ```

6. **Almacenamiento**
   - Scores guardados en base de datos
   - Justificaciones incluidas en el campo `adjustments`
   - Admin puede revisar y ajustar si lo considera necesario

### Ventajas de Groq vs Heurísticas

| Aspecto | Heurísticas | Groq AI |
|---------|-------------|---------|
| Análisis | Keywords simples | Semántico profundo |
| Contextualización | No | Sí (entiende contexto) |
| Rigor | Superficial | Evaluación completa |
| Justificaciones | No automáticas | Sí, provistas por IA |
| Consistencia | Variable | Alta (modelo entrenado) |
| Tiempo | Rápido | Rápido (Groq es muy velocidad) |

### Configuración

**Archivo `.env`**:
```env
GROQ_API_KEY=your_groq_api_key_here
```

**Archivo `evaluation/settings.py`**:
```python
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', 'fallback_key')
```

**Función de evaluación en `evaluation_app/grading.py`**:
```python
from groq import Groq

client = Groq(api_key=settings.GROQ_API_KEY)

def evaluate_with_groq(blog_text, blog_entries, pdf_text):
    # Crear prompt personalizado
    # Llamar a Groq
    # Parsear respuesta JSON
    # Retornar scores
```

### Manejo de Errores

Si Groq falla (API caída, timeout, etc.):
1. Se captura la excepción
2. Se retornan scores por defecto (5/10 para cada criterio)
3. Se registra el error en los logs
4. El admin ve la calificación pero puede revisan manualmente

### Límites y Consideraciones

- **Máximo de caracteres**: Se usan los primeros 3000 caracteres del blog y PDF para no exceder límites de token.
- **Temperatura**: 0.5 (equilibrio entre consistencia y variabilidad).
- **Modelo**: `llama-3.1-8b-instant` (rápido y preciso).
- **Tokens**: ~1000 máx por respuesta.

### Extensiones Futuras

1. **Fine-tuning**: Entrenar Groq con ejemplos históricos de evaluaciones.
2. **Múltiples criterios**: Agregar sub-scores para cada sub-categoría.
3. **Feedback al alumno**: Mostrar justificaciones de Groq al alumno después de publicarse notas.
4. **Análisis de tendencias**: Dashboard para ver distribución de calificaciones.

### Testing

Para probar la función de evaluación:

```bash
# Crear un submission de prueba
python manage.py shell

# En el shell:
from evaluation_app.models import Student, Submission
from evaluation_app.grading import grade_submission

# Crear estudiante y submission de prueba
student = Student.objects.create(name="Test", student_id="TEST001")
submission = Submission.objects.create(
    student=student,
    blog_url="https://ejemplo.com/blog",
    pdf_file="test.pdf"
)

# Evaluar
grade = grade_submission(submission)
print(grade.final_score)
print(grade.adjustments)  # Justificaciones JSON
```

### Notas de Seguridad

- **API Key**: Nunca commitear la API key. Usar `.env` y agregar a `.gitignore`.
- **Privacidad**: Los textos se envían a Groq. Para datos sensibles, revisar política de privacidad.
- **Costos**: Groq es muy económico. El costo estimado por evaluación es <$0.01.

---

**Última actualización**: 23 de marzo de 2026
**Versión**: 1.0 con Groq AI