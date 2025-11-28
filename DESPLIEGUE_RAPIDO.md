# 🚀 Despliegue Rápido en Google Cloud Run

Esta es una guía rápida para desplegar ResQ. Para detalles completos, ver [GUIA_DESPLIEGUE_CLOUD_RUN.md](GUIA_DESPLIEGUE_CLOUD_RUN.md).

## ⚡ Pasos Rápidos

### 1. Prerrequisitos
```bash
# Instalar Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Iniciar sesión y configurar proyecto
gcloud auth login
gcloud config set project TU_PROJECT_ID
```

### 2. Habilitar APIs
```bash
gcloud services enable run.googleapis.com sqladmin.googleapis.com \
    cloudbuild.googleapis.com redis.googleapis.com \
    secretmanager.googleapis.com compute.googleapis.com
```

### 3. Crear Cloud SQL (PostgreSQL)
```bash
gcloud sql instances create resq-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=TU_CONTRASEÑA_SEGURA

gcloud sql databases create resq --instance=resq-postgres
gcloud sql users create app_user --instance=resq-postgres --password=APP_PASSWORD
```

### 4. Crear Redis (Memorystore)
```bash
gcloud redis instances create resq-redis \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_7_0 \
    --tier=basic \
    --network=default
```

### 5. Desplegar (Usando Script)
```bash
# Linux/Mac
chmod +x deploy-cloud-run.sh
./deploy-cloud-run.sh

# Windows
.\deploy-cloud-run.ps1
```

### 6. Desplegar (Manual)
```bash
# Construir y subir imagen
cd ResQ
gcloud builds submit --tag gcr.io/PROJECT_ID/resq-api:latest

# Desplegar
gcloud run deploy resq-api \
    --image gcr.io/PROJECT_ID/resq-api:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 512Mi \
    --add-cloudsql-instances=PROJECT_ID:us-central1:resq-postgres

# Configurar variables de entorno
PROJECT_ID=$(gcloud config get-value project)
REGION=us-central1
CLOUD_SQL_CONNECTION="${PROJECT_ID}:${REGION}:resq-postgres"
REDIS_IP=$(gcloud redis instances describe resq-redis --region=${REGION} --format="value(host)")

gcloud run services update resq-api \
    --region=${REGION} \
    --update-env-vars="DATABASE_URL=postgresql://app_user:APP_PASSWORD@/resq?host=/cloudsql/${CLOUD_SQL_CONNECTION}" \
    --update-env-vars="JWT_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" \
    --update-env-vars="REDIS_HOST=${REDIS_IP}" \
    --update-env-vars="REDIS_PORT=6379"
```

### 7. Verificar
```bash
# Obtener URL
SERVICE_URL=$(gcloud run services describe resq-api --region=us-central1 --format="value(status.url)")

# Probar
curl ${SERVICE_URL}/health
curl ${SERVICE_URL}/

# Ver documentación
echo "Swagger: ${SERVICE_URL}/docs"
```

## 📝 Variables de Entorno Necesarias

- `DATABASE_URL`: Conexión a PostgreSQL
- `JWT_SECRET_KEY`: Clave secreta para JWT
- `JWT_EXPIRE_MINUTES`: Tiempo de expiración (default: 1440)
- `REDIS_HOST`: IP de Redis
- `REDIS_PORT`: Puerto de Redis (default: 6379)
- `REDIS_PASSWORD`: Contraseña de Redis (opcional)
- `REDIS_DB`: Base de datos Redis (default: 0)

## 🔗 Enlaces Útiles

- [Guía Completa](GUIA_DESPLIEGUE_CLOUD_RUN.md)
- [Documentación Cloud Run](https://cloud.google.com/run/docs)
- [Precios GCP](https://cloud.google.com/pricing)


