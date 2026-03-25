"""
grading.py — Evaluación real de blogs de maestría
Extrae cada entrada del blog individualmente y las evalúa con IA.
Implementa exactamente la rúbrica oficial del Seminario de Integración.
"""
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from .models import Grade
from groq import Groq
import json
import re
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

# ──────────────────────────────────────────────
# TABLA PROPORCIONAL OFICIAL DE ENTRADAS
# Fuente: Rúbrica final Detallada Blogs Seminario
# ──────────────────────────────────────────────
TABLA_CANTIDAD = {
    16: 10.0, 15: 9.4, 14: 8.8, 13: 8.1,
    12: 7.5,  11: 6.9, 10: 6.2,
}

def calcular_cantidad_score(n_entradas: int) -> float:
    """Devuelve el puntaje de cantidad según la tabla proporcional oficial."""
    if n_entradas >= 16:
        return 10.0
    if n_entradas in TABLA_CANTIDAD:
        return TABLA_CANTIDAD[n_entradas]
    if n_entradas <= 0:
        return 0.0
    return 5.5  # 9 o menos → ≤5.5


# ──────────────────────────────────────────────
# 1. SCRAPING DEL BLOG — extrae entradas reales
# ──────────────────────────────────────────────
def scrape_blog(url):
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; EvaluationBot/1.0)'}
    try:
        resp = requests.get(url, timeout=15, headers=headers)
        resp.raise_for_status()
    except Exception as e:
        print(f"[scrape_blog] Error fetching {url}: {e}")
        return "", []

    soup = BeautifulSoup(resp.content, 'html.parser')
    entries = []

    # Estrategia 1: Blogspot / Blogger
    posts = soup.select('.post, .hentry, article.post, .blog-post, [itemtype*="BlogPosting"]')
    # Estrategia 2: WordPress
    if not posts:
        posts = soup.select('article, .entry, .post-entry, .type-post')
    # Estrategia 3: Genérico
    if not posts:
        posts = soup.select('[class*="post"], [class*="entry"], [class*="article"]')

    for post in posts[:30]:
        title_el = post.select_one('h1, h2, h3, .post-title, .entry-title, [class*="title"]')
        title = title_el.get_text(strip=True) if title_el else "Sin título"
        if title_el:
            title_el.decompose()
        for tag in post.select('script, style, nav, .sidebar, .widget, .comments, footer'):
            tag.decompose()
        content = re.sub(r'\s+', ' ', post.get_text(separator=' ', strip=True)).strip()
        if len(content) < 30:
            continue
        link_el = post.select_one('a[href]')
        entries.append({
            'title': title[:200],
            'content': content[:2000],
            'url': link_el['href'] if link_el else url,
        })

    if not entries:
        entries = _try_rss_feed(url, headers)

    # Texto general del blog
    for tag in soup.select('script, style, nav, .sidebar, .widget, .navbar, footer, header'):
        tag.decompose()
    blog_text = re.sub(r'\s+', ' ', soup.get_text(separator=' ', strip=True)).strip()

    return blog_text, entries


def _try_rss_feed(url, headers):
    feed_urls = [
        url.rstrip('/') + '/feeds/posts/default?alt=rss',
        url.rstrip('/') + '/feed',
        url.rstrip('/') + '/rss.xml',
    ]
    for feed_url in feed_urls:
        try:
            resp = requests.get(feed_url, timeout=10, headers=headers)
            if resp.status_code == 200:
                fsoup = BeautifulSoup(resp.content, 'xml')
                items = fsoup.find_all('item') or fsoup.find_all('entry')
                entries = []
                for item in items[:20]:
                    title = item.find('title')
                    desc = item.find('description') or item.find('content') or item.find('summary')
                    link = item.find('link')
                    title_text = title.get_text(strip=True) if title else 'Sin título'
                    content_text = ''
                    if desc:
                        inner = BeautifulSoup(desc.get_text(), 'html.parser')
                        content_text = inner.get_text(separator=' ', strip=True)[:2000]
                    if len(content_text) > 30:
                        entries.append({
                            'title': title_text[:200],
                            'content': content_text,
                            'url': link.get_text(strip=True) if link else url,
                        })
                if entries:
                    return entries
        except Exception:
            pass
    return []


# ──────────────────────────────────────────────
# 2. EXTRAER PDF
# ──────────────────────────────────────────────
def extract_pdf(path):
    text = ""
    try:
        with open(path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"[extract_pdf] Error: {e}")
    return text


# ──────────────────────────────────────────────
# 3. EVALUACIÓN CON IA
# ──────────────────────────────────────────────
def _format_entries_for_prompt(entries, max_entries=16, max_chars_each=800):
    lines = []
    for i, e in enumerate(entries[:max_entries], 1):
        lines.append(f"ENTRADA {i}: {e['title']}")
        lines.append(e['content'][:max_chars_each])
        lines.append("---")
    return "\n".join(lines)


def evaluate_with_groq(blog_text, entries, pdf_text, n_entradas_real):
    """
    Evalúa calidad y presentación/protocolo con IA.
    La cantidad YA se calcula con la tabla oficial — la IA solo evalúa calidad,
    presentación y protocolo.
    """
    entries_text = _format_entries_for_prompt(entries)

    # ── Llamada 1: Calidad del contenido ──
    prompt_calidad = f"""Eres un evaluador académico de maestría. Evalúa la CALIDAD del siguiente blog según la rúbrica oficial.

CRITERIO A EVALUAR:
Calidad del Contenido (sobre 10):
- Profundidad analítica: ¿va más allá de lo descriptivo?
- Redacción clara y apropiación conceptual de Métodos Cuantitativos
- Vinculación con el campo profesional (deportes)
- Reflexión crítica y estructura académica

NÚMERO DE ENTRADAS DETECTADAS: {n_entradas_real}

CONTENIDO DE LAS ENTRADAS DEL BLOG:
{entries_text if entries_text else "(No se extrajeron entradas individuales)"}

TEXTO GENERAL DEL BLOG (primeros 2000 caracteres):
{blog_text[:2000]}

Responde SOLO JSON válido:
{{
  "calidad_score": <0-10, un decimal>,
  "justificacion_calidad": "<2-3 oraciones específicas sobre profundidad analítica, redacción y apropiación de Métodos Cuantitativos>"
}}"""

    # ── Llamada 2: Presentación y Protocolo ──
    prompt_pres_prot = f"""Eres un evaluador académico de maestría. Evalúa PRESENTACIÓN y PROTOCOLO del blog según la rúbrica oficial.

CRITERIO 1 — Presentación y Diseño del Blog (sobre 10):
- Cuidado visual, uso de imágenes, tablas, títulos
- Navegación limpia y consistente
- Identidad visual del blog

CRITERIO 2 — Protocolo de Investigación en PDF (sobre 10):
- Claridad metodológica, formulación de variables
- Estructura académica: planteamiento, hipótesis, objetivos, metodología cuantitativa
- Redacción y rigor científico

TEXTO DEL BLOG (primeros 2500 caracteres):
{blog_text[:2500]}

CONTENIDO DEL PDF — PROTOCOLO (primeros 4000 caracteres):
{pdf_text[:4000]}

Responde SOLO JSON válido:
{{
  "presentacion_score": <0-10, un decimal>,
  "protocolo_score": <0-10, un decimal>,
  "justificacion_presentacion": "<2-3 oraciones sobre diseño visual, multimedia, navegación>",
  "justificacion_protocolo": "<2-3 oraciones específicas sobre el protocolo: variables, hipótesis, metodología>"
}}"""

    r1 = _call_groq(prompt_calidad)
    r2 = _call_groq(prompt_pres_prot)

    calidad_score     = float(r1.get("calidad_score", 5.0))
    presentacion_score = float(r2.get("presentacion_score", 5.0))
    protocolo_score   = float(r2.get("protocolo_score", 5.0))

    # Cantidad: se calcula con la tabla oficial
    cantidad_score = calcular_cantidad_score(n_entradas_real)

    combined = {
        "cantidad_score":     cantidad_score,
        "calidad_score":      calidad_score,
        "presentacion_score": presentacion_score,
        "protocolo_score":    protocolo_score,
        "n_entradas":         n_entradas_real,
        "justificaciones": {
            "cantidad":     f"Se detectaron {n_entradas_real} entradas en el blog. "
                           + ("Cumple con las 16 requeridas." if n_entradas_real >= 16
                              else f"Faltan {16 - n_entradas_real} entradas para el máximo."),
            "calidad":      r1.get("justificacion_calidad", "Sin datos"),
            "presentacion": r2.get("justificacion_presentacion", "Sin datos"),
            "protocolo":    r2.get("justificacion_protocolo", "Sin datos"),
        },
    }
    return combined


def _call_groq(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
        )
        text = response.choices[0].message.content
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"[_call_groq] Error: {e}")
    return {}


# ──────────────────────────────────────────────
# 4. FUNCIÓN PRINCIPAL
# ──────────────────────────────────────────────
def grade_submission(submission):
    blog_text, entries = scrape_blog(submission.blog_url)
    pdf_text = extract_pdf(submission.pdf_file.path)
    n_entradas = len(entries)

    scores = evaluate_with_groq(blog_text, entries, pdf_text, n_entradas)

    cantidad_score     = float(scores["cantidad_score"])
    calidad_score      = float(scores["calidad_score"])
    presentacion_score = float(scores["presentacion_score"])
    protocolo_score    = float(scores["protocolo_score"])

    # Ponderación oficial: Cantidad(35%) + Calidad(35%) + Presentación(10%) + Protocolo(20%)
    final_score = (
        cantidad_score     * 0.35 +
        calidad_score      * 0.35 +
        presentacion_score * 0.10 +
        protocolo_score    * 0.20
    )

    return Grade(
        submission=submission,
        blog_score=round((cantidad_score + calidad_score) / 2, 2),
        entries_score=round(protocolo_score, 2),
        total_score=round(final_score, 2),
        final_score=round(final_score, 2),
        adjustments=json.dumps(scores, ensure_ascii=False),
    )
