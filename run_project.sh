#!/bin/bash

# Script para ejecutar el proyecto completo
# Uso: ./run_project.sh [dashboard|streaming|api-test]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt no encontrado. Ejecuta desde la raíz del proyecto"
    exit 1
fi

# Activar virtual environment
print_info "Activando virtual environment..."
source venv/bin/activate

# Instalar dependencias si es necesario
if [ ! -d "venv/lib/python3.9/site-packages/pyspark" ]; then
    print_info "Instalando dependencias..."
    pip install -r requirements.txt
fi

# Obtener comando
COMMAND=${1:-"dashboard"}

case $COMMAND in
    dashboard)
        print_info "Iniciando Dashboard..."
        cd src
        python dashboard.py
        ;;
    streaming)
        print_info "Iniciando Spark Streaming..."
        cd src
        python spark_streaming.py
        ;;
    api-test)
        print_info "Probando conexión a API..."
        cd src
        python api_client.py
        ;;
    all)
        print_info "Iniciando aplicación completa..."
        print_warn "Inicia primero el API en una terminal: ./run_project.sh api-test"
        print_warn "Luego el dashboard en otra: ./run_project.sh dashboard"
        print_warn "Spark Streaming debería ejecutarse en otra: ./run_project.sh streaming"
        ;;
    *)
        print_error "Comando desconocido: $COMMAND"
        echo "Uso: ./run_project.sh [dashboard|streaming|api-test|all]"
        exit 1
        ;;
esac

deactivate
