#!/bin/bash

# Script de ayuda para desplegar ResQ en Google Cloud Run
# Uso: ./deploy-cloud-run.sh

set -e  # Salir si hay algún error

echo "🚀 Script de Despliegue de ResQ en Google Cloud Run"
echo "=================================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud no está instalado${NC}"
    echo "Instala Google Cloud SDK desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Obtener proyecto actual
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: No hay un proyecto configurado${NC}"
    echo "Ejecuta: gcloud config set project PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}✓ Proyecto: ${PROJECT_ID}${NC}"
echo ""

# Configuración
REGION=${REGION:-us-central1}
SERVICE_NAME=${SERVICE_NAME:-resq-api}
CLOUD_SQL_INSTANCE=${CLOUD_SQL_INSTANCE:-resq-postgres}
REDIS_INSTANCE=${REDIS_INSTANCE:-resq-redis}

echo "Configuración:"
echo "  - Región: ${REGION}"
echo "  - Servicio: ${SERVICE_NAME}"
echo "  - Cloud SQL: ${CLOUD_SQL_INSTANCE}"
echo "  - Redis: ${REDIS_INSTANCE}"
echo ""

# Función para construir y subir imagen
build_and_push() {
    echo -e "${YELLOW}📦 Construyendo y subiendo imagen Docker...${NC}"
    gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest
    echo -e "${GREEN}✓ Imagen construida y subida${NC}"
}

# Función para desplegar en Cloud Run
deploy_service() {
    echo -e "${YELLOW}🚀 Desplegando servicio en Cloud Run...${NC}"
    
    gcloud run deploy ${SERVICE_NAME} \
        --image gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest \
        --platform managed \
        --region ${REGION} \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --timeout 300 \
        --max-instances 10 \
        --min-instances 0 \
        --add-cloudsql-instances=${PROJECT_ID}:${REGION}:${CLOUD_SQL_INSTANCE}
    
    echo -e "${GREEN}✓ Servicio desplegado${NC}"
}

# Función para obtener información de Cloud SQL
get_cloud_sql_info() {
    echo -e "${YELLOW}📊 Obteniendo información de Cloud SQL...${NC}"
    
    CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${CLOUD_SQL_INSTANCE}"
    echo "Connection name: ${CLOUD_SQL_CONNECTION_NAME}"
    
    # Verificar que la instancia existe
    if ! gcloud sql instances describe ${CLOUD_SQL_INSTANCE} &>/dev/null; then
        echo -e "${RED}❌ Error: La instancia de Cloud SQL '${CLOUD_SQL_INSTANCE}' no existe${NC}"
        echo "Créala primero con: gcloud sql instances create ${CLOUD_SQL_INSTANCE} ..."
        return 1
    fi
    
    echo -e "${GREEN}✓ Cloud SQL encontrado${NC}"
    return 0
}

# Función para obtener información de Redis
get_redis_info() {
    echo -e "${YELLOW}📊 Obteniendo información de Redis...${NC}"
    
    # Verificar que la instancia existe
    if ! gcloud redis instances describe ${REDIS_INSTANCE} --region=${REGION} &>/dev/null; then
        echo -e "${RED}❌ Error: La instancia de Redis '${REDIS_INSTANCE}' no existe${NC}"
        echo "Créala primero con: gcloud redis instances create ${REDIS_INSTANCE} ..."
        return 1
    fi
    
    REDIS_IP=$(gcloud redis instances describe ${REDIS_INSTANCE} --region=${REGION} --format="value(host)")
    REDIS_PORT=$(gcloud redis instances describe ${REDIS_INSTANCE} --region=${REGION} --format="value(port)")
    
    echo "Redis IP: ${REDIS_IP}"
    echo "Redis Port: ${REDIS_PORT}"
    echo -e "${GREEN}✓ Redis encontrado${NC}"
    return 0
}

# Función para configurar variables de entorno
configure_env_vars() {
    echo -e "${YELLOW}⚙️  Configurando variables de entorno...${NC}"
    
    # Obtener información
    CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${CLOUD_SQL_INSTANCE}"
    REDIS_IP=$(gcloud redis instances describe ${REDIS_INSTANCE} --region=${REGION} --format="value(host)")
    
    # Solicitar valores al usuario
    read -p "Usuario de la base de datos (app_user): " DB_USER
    DB_USER=${DB_USER:-app_user}
    
    read -sp "Contraseña de la base de datos: " DB_PASSWORD
    echo ""
    
    read -p "Nombre de la base de datos (resq): " DB_NAME
    DB_NAME=${DB_NAME:-resq}
    
    read -sp "JWT Secret Key (dejar vacío para generar): " JWT_SECRET
    echo ""
    
    if [ -z "$JWT_SECRET" ]; then
        JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || echo "change-me-in-production")
        echo "JWT Secret generado: ${JWT_SECRET}"
    fi
    
    # Construir DATABASE_URL para Cloud SQL (socket Unix)
    DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@/${DB_NAME}?host=/cloudsql/${CLOUD_SQL_CONNECTION_NAME}"
    
    echo ""
    echo "Configurando variables de entorno..."
    
    gcloud run services update ${SERVICE_NAME} \
        --region=${REGION} \
        --update-env-vars="DATABASE_URL=${DATABASE_URL}" \
        --update-env-vars="JWT_SECRET_KEY=${JWT_SECRET}" \
        --update-env-vars="JWT_EXPIRE_MINUTES=1440" \
        --update-env-vars="REDIS_HOST=${REDIS_IP}" \
        --update-env-vars="REDIS_PORT=6379" \
        --update-env-vars="REDIS_PASSWORD=" \
        --update-env-vars="REDIS_DB=0"
    
    echo -e "${GREEN}✓ Variables de entorno configuradas${NC}"
}

# Función para mostrar información del servicio
show_service_info() {
    echo ""
    echo -e "${YELLOW}📋 Información del Servicio:${NC}"
    echo "=================================="
    
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")
    echo "URL: ${SERVICE_URL}"
    echo "Health Check: ${SERVICE_URL}/health"
    echo "Documentación: ${SERVICE_URL}/docs"
    echo ""
    echo "Para ver logs:"
    echo "  gcloud run services logs read ${SERVICE_NAME} --region=${REGION} --follow"
}

# Menú principal
echo "¿Qué deseas hacer?"
echo "1) Construir y subir imagen Docker"
echo "2) Desplegar servicio en Cloud Run"
echo "3) Configurar variables de entorno"
echo "4) Hacer todo (build + deploy + config)"
echo "5) Ver información del servicio"
echo "6) Ver logs"
echo ""
read -p "Selecciona una opción (1-6): " OPTION

case $OPTION in
    1)
        build_and_push
        ;;
    2)
        get_cloud_sql_info || exit 1
        deploy_service
        ;;
    3)
        get_cloud_sql_info || exit 1
        get_redis_info || exit 1
        configure_env_vars
        ;;
    4)
        get_cloud_sql_info || exit 1
        get_redis_info || exit 1
        build_and_push
        deploy_service
        configure_env_vars
        show_service_info
        ;;
    5)
        show_service_info
        ;;
    6)
        echo -e "${YELLOW}📜 Mostrando logs (Ctrl+C para salir)...${NC}"
        gcloud run services logs read ${SERVICE_NAME} --region=${REGION} --follow
        ;;
    *)
        echo -e "${RED}❌ Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Completado${NC}"


