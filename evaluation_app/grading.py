import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from .models import Grade
from groq import Groq
import json
import re
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def scrape_blog(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        # Extraer entradas: buscar secciones con títulos
        entries = []
        lines = text.split('\n')
        current_entry = ""
        for line in lines:
            if re.match(r'^\d+\.|\w+ \d+|\w+', line.strip()) and len(line.strip()) < 100:
                if current_entry:
                    entries.append(current_entry)
                current_entry = line.strip()
            else:
                current_entry += " " + line.strip()
        if current_entry:
            entries.append(current_entry)
        return text, entries
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return "", []

def extract_pdf(path):
    text = ""
    try:
        with open(path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting PDF {path}: {e}")
    return text

def evaluate_with_groq(blog_text, blog_entries, pdf_text):
    """Use Groq AI to evaluate content based on rubric"""
    rubric_prompt = f"""Evalúa el siguiente contenido de un blog de maestría en Métodos Cuantitativos según esta rúbrica:

1. Cantidad y Regularidad de Entregas (35%): Evalúa si hay aproximadamente 16 entradas temáticas. El blog tiene {len(blog_entries)} entradas detectadas.
2. Calidad del Contenido (35%): Evalúa profundidad analítica, redacción clara, apropiación conceptual de métodos cuantitativos, estructura.
3. Presentación y Diseño del Blog (10%): Evalúa cuidado visual, uso de imágenes, tablas, navegación.
4. Protocolo de Investigación (20%): Evalúa claridad metodológica, formulación de variables, estructura académica en el PDF.

CONTENIDO DEL BLOG (primeros 3000 caracteres):
{blog_text[:3000]}

CONTENIDO DEL PDF (primeros 3000 caracteres):
{pdf_text[:3000]}

Responde SOLO en JSON válido con este formato exacto (sin texto adicional, sin markdown):
{{
  "cantidad_score": <número 0-10>,
  "calidad_score": <número 0-10>,
  "presentacion_score": <número 0-10>,
  "protocolo_score": <número 0-10>,
  "justificaciones": {{
    "cantidad": "<breve justificación>",
    "calidad": "<breve justificación>",
    "presentacion": "<breve justificación>",
    "protocolo": "<breve justificación>"
  }}
}}"""
    
    try:
        message = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": rubric_prompt}],
            temperature=0.5,
            max_tokens=1024,
        )
        response_text = message.choices[0].message.content
        # Extraer JSON de la respuesta
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            scores = json.loads(json_match.group())
            return scores
        else:
            # Fallback: scores por defecto si falla el parsing
            return {
                "cantidad_score": 5,
                "calidad_score": 5,
                "presentacion_score": 5,
                "protocolo_score": 5,
                "justificaciones": {"cantidad": "Error parsing", "calidad": "Error parsing", "presentacion": "Error parsing", "protocolo": "Error parsing"}
            }
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return {
            "cantidad_score": 5,
            "calidad_score": 5,
            "presentacion_score": 5,
            "protocolo_score": 5,
            "justificaciones": {"cantidad": f"Error API: {str(e)}", "calidad": f"Error API: {str(e)}", "presentacion": f"Error API: {str(e)}", "protocolo": f"Error API: {str(e)}"}
        }

def grade_submission(submission):
    blog_text, blog_entries = scrape_blog(submission.blog_url)
    pdf_text = extract_pdf(submission.pdf_file.path)
    
    # Usar Groq para evaluar
    scores = evaluate_with_groq(blog_text, blog_entries, pdf_text)
    
    cantidad_score = scores.get("cantidad_score", 5)
    calidad_score = scores.get("calidad_score", 5)
    presentacion_score = scores.get("presentacion_score", 5)
    protocolo_score = scores.get("protocolo_score", 5)
    justificaciones = json.dumps(scores.get("justificaciones", {}))
    
    # Ponderaciones de Rúbrica: (Cantidad × 0.35) + (Calidad × 0.35) + (Presentación × 0.10) + (Protocolo × 0.20)
    final_score = (cantidad_score * 0.35) + (calidad_score * 0.35) + (presentacion_score * 0.10) + (protocolo_score * 0.20)
    
    return Grade(
        submission=submission,
        blog_score=(cantidad_score + calidad_score + presentacion_score) / 3,
        entries_score=protocolo_score,
        total_score=final_score,
        final_score=final_score,
        adjustments=justificaciones
    )