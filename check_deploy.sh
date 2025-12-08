#!/bin/bash
# Script de verificación pre-deploy para Railway

echo "=========================================="
echo "   🔍 VERIFICACIÓN PRE-DEPLOY RAILWAY"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 ${RED}(FALTA)${NC}"
        return 1
    fi
}

ALL_OK=true

# Verificar archivos obligatorios
echo "📄 Archivos de configuración:"
check_file "requirements.txt" || ALL_OK=false
check_file "requirements-railway.txt" || ALL_OK=false
check_file "runtime.txt" || ALL_OK=false
check_file "Procfile" || ALL_OK=false
check_file "nixpacks.toml" || ALL_OK=false
check_file ".gitignore" || ALL_OK=false
check_file "manage.py" || ALL_OK=false
echo ""

# Verificar settings
echo "⚙️  Configuración Django:"
check_file "backend_salessmart/settings.py" || ALL_OK=false
check_file "backend_salessmart/wsgi.py" || ALL_OK=false
echo ""

# Verificar apps principales
echo "📦 Apps principales:"
check_file "users/models.py" || ALL_OK=false
check_file "products/models.py" || ALL_OK=false
check_file "sales/models.py" || ALL_OK=false
echo ""

# Scripts útiles
echo "🛠️  Scripts útiles:"
check_file "create_superuser.py"
check_file "users/management/commands/generate_users.py"
check_file "sales/management/commands/generate_orders.py"
echo ""

# Variables de entorno necesarias
echo "🔐 Variables de entorno necesarias en Railway:"
echo -e "${YELLOW}⚠${NC}  SECRET_KEY"
echo -e "${YELLOW}⚠${NC}  DATABASE_URL (auto-generada por PostgreSQL)"
echo -e "${YELLOW}⚠${NC}  DEBUG=False"
echo -e "${YELLOW}⚠${NC}  ALLOWED_HOSTS=*.railway.app"
echo ""

if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}=========================================="
    echo -e "   ✅ TODO LISTO PARA DEPLOY"
    echo -e "==========================================${NC}"
    echo ""
    echo "Próximos pasos:"
    echo "1. git push origin main"
    echo "2. Crear proyecto en Railway"
    echo "3. Agregar PostgreSQL"
    echo "4. Configurar variables de entorno"
    echo "5. ¡Deploy automático!"
else
    echo -e "${RED}=========================================="
    echo -e "   ❌ FALTAN ARCHIVOS REQUERIDOS"
    echo -e "==========================================${NC}"
    echo ""
    echo "Por favor, verifica los archivos marcados con ✗"
fi
