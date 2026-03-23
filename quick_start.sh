#!/bin/bash
# Quick Start Script para Evalaución Maestría Anahuac
# Ejecutar: bash quick_start.sh

echo "============================================================"
echo "🎓 EVALUACIÓN DE BLOGS - QUICK START"
echo "============================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "${YELLOW}1. Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python3 encontrado: $(python3 --version)${NC}"
echo ""

# Install dependencies
echo -e "${YELLOW}2. Instalando dependencias...${NC}"
python3 -m pip install -r requirements.txt -q
echo -e "${GREEN}✓ Dependencias instaladas${NC}"
echo ""

# Create .env if not exists
echo -e "${YELLOW}3. Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    echo "GROQ_API_KEY=your_groq_api_key_here" > .env
    echo -e "${GREEN}✓ Archivo .env creado${NC}"
else
    echo -e "${GREEN}✓ Archivo .env ya existe${NC}"
fi
echo ""

# Database migrations
echo -e "${YELLOW}4. Inicializando base de datos...${NC}"
python3 manage.py migrate -q
echo -e "${GREEN}✓ Base de datos lista${NC}"
echo ""

# Test Groq
echo -e "${YELLOW}5. Verificando conexión a Groq AI...${NC}"
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evaluation.settings')
django.setup()
from django.conf import settings
from groq import Groq
try:
    client = Groq(api_key=settings.GROQ_API_KEY)
    print('✓ Conexión a Groq AI: EXITOSA')
except Exception as e:
    print(f'❌ Error: {e}')
"
echo ""

echo "============================================================"
echo -e "${GREEN}🎯 PASOS SIGUIENTES:${NC}"
echo "============================================================"
echo ""
echo "1. Crear superusuario (admin):"
echo "   ${YELLOW}python3 manage.py createsuperuser${NC}"
echo ""
echo "2. Iniciar servidor:"
echo "   ${YELLOW}python3 manage.py runserver${NC}"
echo ""
echo "3. Acceder a:"
echo "   - Formulario de alumnos: ${YELLOW}http://127.0.0.1:8000/submit/${NC}"
echo "   - Panel de admin: ${YELLOW}http://127.0.0.1:8000/admin/${NC}"
echo "   - Exportar Excel: ${YELLOW}http://127.0.0.1:8000/export/${NC}"
echo ""
echo "4. (Opcional) Ejecutar pruebas:"
echo "   ${YELLOW}python3 test_groq.py${NC}"
echo ""
echo "============================================================"
echo -e "${GREEN}✅ LISTO PARA COMENZAR${NC}"
echo "============================================================"