#!/usr/bin/env python3
"""
Script de prueba para verificar que Groq está correctamente integrado.
Ejecutar: python3 test_groq.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evaluation.settings')
django.setup()

from django.conf import settings
from groq import Groq

def test_groq_connection():
    """Prueba que Groq está bien configurado y responde."""
    print("=" * 60)
    print("PRUEBA DE CONEXIÓN A GROQ")
    print("=" * 60)
    
    api_key = settings.GROQ_API_KEY
    if not api_key:
        print("❌ ERROR: GROQ_API_KEY no está configurada")
        return False
    
    print(f"✓ API Key cargada: {api_key[:20]}...{api_key[-10:]}")
    
    try:
        client = Groq(api_key=api_key)
        
        # Prueba simple
        test_prompt = "Responde con un JSON simple: {\"status\": \"ok\"}"
        
        print("\nEnviando mensaje de prueba a Groq...")
        message = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": test_prompt}],
            temperature=0.5,
            max_tokens=100,
        )
        
        response = message.choices[0].message.content
        print(f"✓ Respuesta recibida: {response[:100]}")
        print("\n✓ CONEXIÓN A GROQ: EXITOSA")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_grading_function():
    """Prueba la función de calificación con datos ficticios."""
    print("\n" + "=" * 60)
    print("PRUEBA DE FUNCIÓN DE CALIFICACIÓN")
    print("=" * 60)
    
    from evaluation_app.grading import evaluate_with_groq
    
    blog_text = """
    Métodos Cuantitativos en Investigación
    
    La investigación cuantitativa utiliza análisis estadísticos y matemáticos.
    Se emplean variables medibles, regresiones lineales, ANOVA, correlaciones.
    La hipótesis se formula de manera precisa y se contrasta estadísticamente.
    Los datos se recopilan sistemáticamente usando instrumentos validados.
    El análisis requiere software como SPSS, R, Python con pandas y scipy.
    """
    
    pdf_text = """
    PROTOCOLO DE INVESTIGACIÓN
    
    Título: Análisis de Factores de Éxito en Proyectos de IA
    
    Variables Independientes:
    - Experiencia del equipo (años)
    - Inversión inicial (millones USD)
    - Duración del proyecto (meses)
    
    Variables Dependientes:
    - Tasa de éxito (%)
    - Tiempo de implementación
    - Satisfacción de usuarios (escala 1-10)
    
    Metodología: Regresión logística multinomial
    Muestra: 150 proyectos de diferentes industrias
    """
    
    blog_entries = ["Entrada 1", "Entrada 2", "Entrada 3", "Entrada 4", "Entrada 5"]
    
    print("Enviando datos ficticios para evaluación...")
    print(f"- Blog entries: {len(blog_entries)}")
    print(f"- Blog text: {len(blog_text)} caracteres")
    print(f"- PDF text: {len(pdf_text)} caracteres")
    
    try:
        scores = evaluate_with_groq(blog_text, blog_entries, pdf_text)
        
        print("\n✓ SCORES RECIBIDOS:")
        print(f"  - Cantidad: {scores.get('cantidad_score', 'N/A')}/10")
        print(f"  - Calidad: {scores.get('calidad_score', 'N/A')}/10")
        print(f"  - Presentación: {scores.get('presentacion_score', 'N/A')}/10")
        print(f"  - Protocolo: {scores.get('protocolo_score', 'N/A')}/10")
        
        print("\n✓ JUSTIFICACIONES:")
        just = scores.get('justificaciones', {})
        for key, value in just.items():
            print(f"  - {key}: {value[:50]}...")
        
        # Calcular final
        final = (scores.get('cantidad_score', 5) * 0.35 + 
                 scores.get('calidad_score', 5) * 0.35 + 
                 scores.get('presentacion_score', 5) * 0.10 + 
                 scores.get('protocolo_score', 5) * 0.20)
        
        print(f"\n✓ CALIFICACIÓN FINAL: {final:.2f}/10")
        print("\n✓ FUNCIÓN DE CALIFICACIÓN: EXITOSA")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SUITE DE PRUEBAS: INTEGRACIÓN GROQ IA")
    print("=" * 60 + "\n")
    
    # Test 1
    conn_ok = test_groq_connection()
    
    # Test 2
    if conn_ok:
        grade_ok = test_grading_function()
    else:
        grade_ok = False
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"✓ Conexión a Groq: {'EXITOSA' if conn_ok else 'FALLIDA'}")
    print(f"✓ Función de calificación: {'EXITOSA' if grade_ok else 'FALLIDA'}")
    print("\n" + "=" * 60)
    
    sys.exit(0 if (conn_ok and grade_ok) else 1)