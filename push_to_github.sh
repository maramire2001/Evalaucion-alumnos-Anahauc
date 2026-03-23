#!/bin/bash
# ============================================================
# Script para hacer Push a GitHub y Deploy en Render
# ============================================================

set -e  # Exit si algo falla

echo ""
echo "============================================================"
echo "🚀 GITHUB PUSH + RENDER DEPLOY SCRIPT"
echo "============================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================
# PASO 1: Verificar que GitHub URL está configurada
# ============================================================

echo -e "${YELLOW}PASO 1: Verificar configuración de Git${NC}"
echo ""

# Verificar si origin existe
if git remote get-url origin &> /dev/null; then
    REMOTE_URL=$(git remote get-url origin)
    echo -e "${GREEN}✓ Remote 'origin' encontrado:${NC}"
    echo "  $REMOTE_URL"
else
    echo -e "${RED}❌ Remote 'origin' NO configurado${NC}"
    echo ""
    echo "Debes agregar el remote antes de correr este script:"
    echo ""
    echo -e "${BLUE}git remote add origin https://github.com/TU_USUARIO/evaluacion-maestria-anahuac.git${NC}"
    echo ""
    exit 1
fi

echo ""

# ============================================================
# PASO 2: Verificar que no hay cambios sin commitear
# ============================================================

echo -e "${YELLOW}PASO 2: Verificar estado del repositorio${NC}"
echo ""

if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ Hay cambios sin commitear:${NC}"
    echo ""
    git status --short
    echo ""
    echo "Debes hacer commit primero:"
    echo -e "${BLUE}git add .${NC}"
    echo -e "${BLUE}git commit -m 'Tu mensaje de commit'${NC}"
    echo ""
    exit 1
else
    echo -e "${GREEN}✓ Repositorio limpio (todos los cambios commiteados)${NC}"
fi

echo ""

# ============================================================
# PASO 3: Preparar branch main
# ============================================================

echo -e "${YELLOW}PASO 3: Preparar branch${NC}"
echo ""

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Branch actual: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}Cambiando a branch 'main'...${NC}"
    git checkout -b main 2>/dev/null || git checkout main
fi

echo -e "${GREEN}✓ En branch 'main'${NC}"
echo ""

# ============================================================
# PASO 4: Hacer Push a GitHub
# ============================================================

echo -e "${YELLOW}PASO 4: Hacer Push a GitHub${NC}"
echo ""
echo "Esto te pedirá tu token de GitHub o contraseña..."
echo ""

git push -u origin main

echo ""
echo -e "${GREEN}✓ ¡Push a GitHub exitoso!${NC}"
echo ""

# ============================================================
# PASO 5: Mostrar instrucciones para Render
# ============================================================

echo "============================================================"
echo -e "${BLUE}🎉 ¡CÓDIGO EN GITHUB!${NC}"
echo "============================================================"
echo ""

echo -e "${YELLOW}PRÓXIMO PASO: Configurar Deploy en Render${NC}"
echo ""

echo "1. Ve a: https://render.com/dashboard"
echo ""

echo "2. Click en 'New +' → selecciona 'Web Service'"
echo ""

echo "3. Selecciona 'Connect a repository'"
echo ""

echo "4. Busca y selecciona:"
echo -e "   ${BLUE}evaluacion-maestria-anahuac${NC}"
echo ""

echo "5. Completa la configuración:"
echo ""
echo -e "   ${BLUE}Build Command:${NC}"
echo "   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --no-input"
echo ""
echo -e "   ${BLUE}Start Command:${NC}"
echo "   gunicorn evaluation.wsgi"
echo ""

echo "6. Agrega estas variables de entorno:"
echo ""
echo -e "   ${BLUE}GROQ_API_KEY${NC}="
echo "   your_groq_api_key_here"
echo ""
echo -e "   ${BLUE}DEBUG${NC}=False"
echo ""
echo -e "   ${BLUE}SECRET_KEY${NC}=<generar con Python>"
echo "   (Ver instrucciones en DEPLOYMENT_GUIDE.md)"
echo ""

echo "7. Click 'Create Web Service' y espera ~3 minutos"
echo ""

echo -e "${GREEN}✓ Script completado${NC}"
echo ""
echo "============================================================"