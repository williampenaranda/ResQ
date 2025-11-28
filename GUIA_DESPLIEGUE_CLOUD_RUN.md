# 🚀 Guía de Despliegue en Google Cloud Run

Esta guía te llevará paso a paso para desplegar el sistema ResQ en Google Cloud Run, incluyendo la configuración de PostgreSQL (Cloud SQL), Redis (Memorystore) y todas las variables de entorno necesarias.

---

## 📋 Tabla de Contenidos

1. [Prerrequisitos](#1-prerrequisitos)
2. [Configuración Inicial de Google Cloud](#2-configuración-inicial-de-google-cloud)
3. [Crear Base de Datos PostgreSQL (Cloud SQL)](#3-crear-base-de-datos-postgresql-cloud-sql)
4. [Crear Instancia de Redis (Memorystore)](#4-crear-instancia-de-redis-memorystore)
5. [Preparar el Código para Despliegue](#5-preparar-el-código-para-despliegue)
6. [Configurar Google Cloud Build](#6-configurar-google-cloud-build)
7. [Desplegar en Cloud Run](#7-desplegar-en-cloud-run)
8. [Configurar Variables de Entorno](#8-configurar-variables-de-entorno)
9. [Configurar Conexión a Cloud SQL](#9-configurar-conexión-a-cloud-sql)
10. [Verificar el Despliegue](#10-verificar-el-despliegue)
11. [Solución de Problemas](#11-solución-de-problemas)

---

## 1. Prerrequisitos

Antes de comenzar, asegúrate de tener:

- ✅ Una cuenta de Google Cloud Platform (GCP) con facturación habilitada
- ✅ Google Cloud SDK (gcloud) instalado en tu máquina
- ✅ Docker instalado (opcional, para pruebas locales)
- ✅ Git instalado
- ✅ Acceso a una terminal/consola

### Instalar Google Cloud SDK

**Windows:**
1. Descargar desde: https://cloud.google.com/sdk/docs/install
2. Ejecutar el instalador
3. Abrir PowerShell y ejecutar: `gcloud init`

**Linux/Mac:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

---

## 2. Configuración Inicial de Google Cloud

### 2.1 Iniciar Sesión y Configurar Proyecto

```bash
# Iniciar sesión en Google Cloud
gcloud auth login

# Listar proyectos disponibles
gcloud projects list

# Configurar el proyecto (reemplaza PROJECT_ID con tu ID de proyecto)
gcloud config set project PROJECT_ID

# O crear un nuevo proyecto
gcloud projects create resq-project --name="ResQ System"
gcloud config set project resq-project

# Habilitar facturación (necesario para Cloud Run, Cloud SQL y Memorystore)
# Esto se hace desde la consola web: https://console.cloud.google.com/billing
```

### 2.2 Habilitar APIs Necesarias

```bash
# Habilitar Cloud Run API
gcloud services enable run.googleapis.com

# Habilitar Cloud SQL Admin API
gcloud services enable sqladmin.googleapis.com

# Habilitar Cloud Build API (para construir imágenes Docker)
gcloud services enable cloudbuild.googleapis.com

# Habilitar Memorystore API (para Redis)
gcloud services enable redis.googleapis.com

# Habilitar Secret Manager API (recomendado para secretos)
gcloud services enable secretmanager.googleapis.com

# Habilitar Compute Engine API (requerido por Memorystore)
gcloud services enable compute.googleapis.com
```

---

## 3. Crear Base de Datos PostgreSQL (Cloud SQL)

### 3.1 Crear Instancia de Cloud SQL

```bash
# Crear instancia de Cloud SQL para PostgreSQL
gcloud sql instances create resq-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=TU_CONTRASEÑA_SEGURA_AQUI \
    --storage-type=SSD \
    --storage-size=20GB \
    --backup-start-time=03:00 \
    --enable-bin-log
```

**Nota:** 
- `db-f1-micro` es el tier más económico (solo para desarrollo/pruebas)
- Para producción, considera `db-n1-standard-1` o superior
- Reemplaza `TU_CONTRASEÑA_SEGURA_AQUI` con una contraseña segura
- Anota esta contraseña, la necesitarás más adelante

### 3.2 Crear Base de Datos

```bash
# Crear la base de datos
gcloud sql databases create resq --instance=resq-postgres
```

### 3.3 Crear Usuario para la Aplicación

```bash
# Crear usuario (reemplaza 'app_user' y 'app_password' con valores seguros)
gcloud sql users create app_user \
    --instance=resq-postgres \
    --password=app_password
```

### 3.4 Obtener la IP de la Instancia

```bash
# Obtener la IP pública de la instancia
gcloud sql instances describe resq-postgres --format="value(ipAddresses[0].ipAddress)"
```

Anota esta IP, la necesitarás para la cadena de conexión.

### 3.5 Configurar Red (Opcional pero Recomendado)

Para mayor seguridad, puedes configurar la instancia para que solo acepte conexiones desde Cloud Run usando una red privada. Esto requiere configuración adicional de VPC.

**Para desarrollo, puedes usar la IP pública con autorización de IPs.**

---

## 4. Crear Instancia de Redis (Memorystore)

### 4.1 Crear Instancia de Memorystore para Redis

```bash
# Crear instancia de Redis
gcloud redis instances create resq-redis \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_7_0 \
    --tier=basic \
    --network=default
```

**Nota:**
- `--size=1` es 1GB (mínimo, solo para desarrollo)
- Para producción, considera tamaños mayores
- `--tier=basic` es el más económico
- `--network=default` usa la red por defecto

### 4.2 Obtener Información de la Instancia

```bash
# Obtener la IP y puerto de Redis
gcloud redis instances describe resq-redis --region=us-central1 --format="value(host,port)"
```

Anota estos valores (IP y puerto, generalmente 6379).

---

## 5. Preparar el Código para Despliegue

### 5.1 Verificar que Existen los Archivos Necesarios

Asegúrate de que en la carpeta `ResQ/` existan:
- ✅ `Dockerfile` (ya creado)
- ✅ `.dockerignore` (ya creado)
- ✅ `requirements.txt`
- ✅ `src/main.py`

### 5.2 Probar el Dockerfile Localmente (Opcional)

```bash
# Navegar a la carpeta del proyecto
cd ResQ

# Construir la imagen Docker
docker build -t resq-api:local .

# Probar la imagen (necesitarás configurar variables de entorno)
docker run -p 8000:8000 \
    -e DATABASE_URL="postgresql://user:pass@host:5432/resq" \
    -e JWT_SECRET_KEY="test-key" \
    -e REDIS_HOST="localhost" \
    -e REDIS_PORT="6379" \
    resq-api:local
```

---

## 6. Configurar Google Cloud Build

### 6.1 Crear Archivo cloudbuild.yaml (Opcional)

Puedes crear un archivo `cloudbuild.yaml` en la raíz del proyecto para automatizar el build:

```yaml
steps:
  # Construir la imagen Docker
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/resq-api:$SHORT_SHA', '.']
  
  # Subir la imagen a Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/resq-api:$SHORT_SHA']
  
  # Desplegar en Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'resq-api'
      - '--image'
      - 'gcr.io/$PROJECT_ID/resq-api:$SHORT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
```

### 6.2 Habilitar Container Registry

```bash
# Habilitar Container Registry API
gcloud services enable containerregistry.googleapis.com
```

---

## 7. Desplegar en Cloud Run

### 7.1 Construir y Subir la Imagen

```bash
# Navegar a la carpeta del proyecto
cd ResQ

# Configurar Docker para usar gcloud como helper
gcloud auth configure-docker

# Construir y subir la imagen a Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/resq-api:latest
```

Reemplaza `PROJECT_ID` con tu ID de proyecto.

### 7.2 Desplegar el Servicio en Cloud Run

```bash
# Desplegar el servicio
gcloud run deploy resq-api \
    --image gcr.io/PROJECT_ID/resq-api:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0
```

**Parámetros importantes:**
- `--memory 512Mi`: Memoria asignada (ajusta según necesidades)
- `--cpu 1`: CPU asignada
- `--timeout 300`: Timeout de 5 minutos (útil para WebSockets)
- `--max-instances 10`: Máximo de instancias concurrentes
- `--min-instances 0`: Escala a cero cuando no hay tráfico (ahorra costos)

---

## 8. Configurar Variables de Entorno

### 8.1 Obtener la Cadena de Conexión de Cloud SQL

Primero, necesitas construir la cadena de conexión. Para Cloud SQL, hay dos opciones:

**Opción A: Usar Socket Unix (Recomendado para producción)**
```bash
# Obtener el nombre de conexión
PROJECT_ID=$(gcloud config get-value project)
REGION=us-central1
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:resq-postgres"

# La cadena de conexión será:
# DATABASE_URL=postgresql://app_user:app_password@/resq?host=/cloudsql/${CLOUD_SQL_CONNECTION_NAME}
```

**⚠️ IMPORTANTE:** Para usar el socket Unix, debes:
1. Configurar la conexión en Cloud Run (ver paso 9.1)
2. El formato de la URL es: `postgresql://user:password@/database?host=/cloudsql/PROJECT:REGION:INSTANCE`

**Opción B: Usar IP Pública (Más simple para desarrollo)**
```bash
# Obtener la IP pública
CLOUD_SQL_IP=$(gcloud sql instances describe resq-postgres --format="value(ipAddresses[0].ipAddress)")

# Autorizar la IP (solo para desarrollo, no recomendado para producción)
gcloud sql instances patch resq-postgres --authorized-networks=0.0.0.0/0

# La cadena de conexión será:
# DATABASE_URL=postgresql://app_user:app_password@${CLOUD_SQL_IP}:5432/resq
```

**⚠️ ADVERTENCIA:** Autorizar `0.0.0.0/0` permite conexiones desde cualquier IP. Solo úsalo para desarrollo.

### 8.2 Obtener Información de Redis

```bash
# Obtener IP de Redis
REDIS_IP=$(gcloud redis instances describe resq-redis --region=us-central1 --format="value(host)")

# El puerto generalmente es 6379
REDIS_PORT=6379
```

### 8.3 Generar JWT Secret Key

```bash
# Generar una clave secreta segura
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Anota esta clave.

### 8.4 Configurar Variables de Entorno en Cloud Run

```bash
# Obtener valores necesarios
PROJECT_ID=$(gcloud config get-value project)
REGION=us-central1
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:resq-postgres"
REDIS_IP=$(gcloud redis instances describe resq-redis --region=${REGION} --format="value(host)")

# Actualizar el servicio con las variables de entorno
gcloud run services update resq-api \
    --region=${REGION} \
    --set-env-vars="DATABASE_URL=postgresql://app_user:app_password@/resq?host=/cloudsql/${CLOUD_SQL_CONNECTION_NAME}" \
    --set-env-vars="JWT_SECRET_KEY=TU_CLAVE_SECRETA_AQUI" \
    --set-env-vars="JWT_EXPIRE_MINUTES=1440" \
    --set-env-vars="REDIS_HOST=${REDIS_IP}" \
    --set-env-vars="REDIS_PORT=6379" \
    --set-env-vars="REDIS_PASSWORD=" \
    --set-env-vars="REDIS_DB=0"
```

**⚠️ IMPORTANTE:** Reemplaza:
- `app_user` y `app_password` con los valores que creaste en el paso 3.3
- `TU_CLAVE_SECRETA_AQUI` con la clave generada en el paso 8.3

### 8.5 Usar Secret Manager (Recomendado para Producción)

Para mayor seguridad, puedes almacenar secretos en Secret Manager:

```bash
# Crear secretos
echo -n "app_password" | gcloud secrets create db-password --data-file=-
echo -n "TU_CLAVE_SECRETA_AQUI" | gcloud secrets create jwt-secret --data-file=-

# Dar permisos a Cloud Run para acceder a los secretos
gcloud secrets add-iam-policy-binding db-password \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding jwt-secret \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Actualizar Cloud Run para usar secretos
gcloud run services update resq-api \
    --region=${REGION} \
    --update-secrets="DATABASE_PASSWORD=db-password:latest,JWT_SECRET_KEY=jwt-secret:latest" \
    --set-env-vars="DATABASE_URL=postgresql://app_user:$(gcloud secrets versions access latest --secret=db-password)@/resq?host=/cloudsql/${CLOUD_SQL_CONNECTION_NAME}"
```

---

## 9. Configurar Conexión a Cloud SQL

### 9.1 Habilitar Cloud SQL Connection en Cloud Run

Para que Cloud Run pueda conectarse a Cloud SQL usando el socket Unix (más seguro):

```bash
# Actualizar el servicio para agregar la conexión a Cloud SQL
gcloud run services update resq-api \
    --region=us-central1 \
    --add-cloudsql-instances=${PROJECT_ID}:${REGION}:resq-postgres
```

### 9.2 Configurar Autorización de IPs (Alternativa)

Si prefieres usar la IP pública:

```bash
# Obtener el rango de IPs de Cloud Run
# Cloud Run usa IPs dinámicas, así que necesitas autorizar un rango amplio
# O mejor, usar el socket Unix como en 9.1

# Autorizar una IP específica (no recomendado para Cloud Run)
gcloud sql instances patch resq-postgres --authorized-networks=0.0.0.0/0
```

**⚠️ Advertencia:** Autorizar `0.0.0.0/0` permite conexiones desde cualquier IP. Solo úsalo para desarrollo.

### 9.3 Instalar Cloud SQL Proxy en el Contenedor (Opcional)

Si decides usar Cloud SQL Proxy, necesitas modificar el Dockerfile:

```dockerfile
# Agregar al Dockerfile antes del CMD
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy && \
    chmod +x cloud_sql_proxy

# Y modificar el CMD para iniciar el proxy en background
CMD ./cloud_sql_proxy -instances=PROJECT_ID:REGION:INSTANCE_NAME=tcp:5432 & \
    uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**Nota:** El método del socket Unix (paso 9.1) es más simple y recomendado.

---

## 10. Verificar el Despliegue

### 10.1 Obtener la URL del Servicio

```bash
# Obtener la URL del servicio desplegado
gcloud run services describe resq-api --region=us-central1 --format="value(status.url)"
```

### 10.2 Probar el Endpoint de Health Check

```bash
# Obtener la URL
SERVICE_URL=$(gcloud run services describe resq-api --region=us-central1 --format="value(status.url)")

# Probar el endpoint de health
curl ${SERVICE_URL}/health

# Probar el endpoint raíz
curl ${SERVICE_URL}/

# Ver la documentación Swagger
# Abre en el navegador: ${SERVICE_URL}/docs
```

### 10.3 Ver Logs

```bash
# Ver logs en tiempo real
gcloud run services logs read resq-api --region=us-central1 --follow

# Ver logs de los últimos 100 registros
gcloud run services logs read resq-api --region=us-central1 --limit=100
```

### 10.4 Verificar Conexión a Base de Datos

Los logs deberían mostrar:
```
Base de datos lista
```

Si hay errores de conexión, revisa:
- La cadena de conexión en las variables de entorno
- Que Cloud SQL esté configurado correctamente (paso 9.1)
- Que las credenciales sean correctas

### 10.5 Verificar Conexión a Redis

Los logs deberían mostrar que Redis está conectado. Si hay advertencias, verifica:
- La IP y puerto de Redis en las variables de entorno
- Que Memorystore esté en la misma región que Cloud Run
- Que la red esté configurada correctamente

---

## 11. Solución de Problemas

### Error: "No se puede conectar a la base de datos"

**Causas posibles:**
1. Cloud SQL no está configurado en Cloud Run
   - Solución: Ejecutar paso 9.1

2. Credenciales incorrectas
   - Solución: Verificar usuario y contraseña en variables de entorno

3. Base de datos no existe
   - Solución: Ejecutar paso 3.2

4. Formato incorrecto de DATABASE_URL
   - Para socket Unix: `postgresql://user:pass@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE`
   - Para IP pública: `postgresql://user:pass@IP:5432/dbname`

### Error: "Redis connection refused"

**Causas posibles:**
1. Redis no está en la misma región
   - Solución: Asegúrate de que Memorystore y Cloud Run estén en la misma región

2. IP incorrecta de Redis
   - Solución: Verificar con `gcloud redis instances describe resq-redis --region=REGION`

3. Red no configurada
   - Solución: Asegúrate de que Memorystore use la red `default` o la misma VPC que Cloud Run

### Error: "Permission denied" o "Access denied"

**Causas posibles:**
1. APIs no habilitadas
   - Solución: Ejecutar paso 2.2

2. Permisos insuficientes
   - Solución: Verificar que la cuenta de servicio tenga los permisos necesarios

### El servicio no inicia

**Verificar:**
1. Logs de Cloud Run: `gcloud run services logs read resq-api --region=us-central1`
2. Que el Dockerfile esté correcto
3. Que todas las dependencias estén en `requirements.txt`
4. Que el puerto esté configurado correctamente (Cloud Run usa la variable `PORT`)

### WebSockets no funcionan

**Nota importante:** Cloud Run tiene limitaciones con WebSockets de larga duración. Para WebSockets persistentes, considera:
- Usar Cloud Run con `--min-instances=1` para evitar cold starts
- O migrar a Google Kubernetes Engine (GKE) para mejor soporte de WebSockets

---

## 📝 Checklist Final

Antes de considerar el despliegue completo, verifica:

- [ ] Cloud SQL está creado y funcionando
- [ ] Memorystore (Redis) está creado y funcionando
- [ ] Cloud Run está desplegado y accesible
- [ ] Variables de entorno están configuradas correctamente
- [ ] Conexión a Cloud SQL está configurada (socket Unix o IP)
- [ ] Health check responde correctamente (`/health`)
- [ ] Swagger UI es accesible (`/docs`)
- [ ] Logs no muestran errores críticos
- [ ] Base de datos se inicializa correctamente (tablas creadas)
- [ ] Redis está conectado (sin advertencias en logs)

---

## 🛠️ Scripts de Ayuda

He creado scripts para facilitar el despliegue:

### Script para Linux/Mac (Bash)
```bash
# Dar permisos de ejecución
chmod +x deploy-cloud-run.sh

# Ejecutar
./deploy-cloud-run.sh
```

### Script para Windows (PowerShell)
```powershell
# Ejecutar
.\deploy-cloud-run.ps1
```

Los scripts te permiten:
- Construir y subir la imagen Docker
- Desplegar el servicio en Cloud Run
- Configurar variables de entorno interactivamente
- Ver información del servicio y logs

---

## 🔄 Actualizar el Despliegue

Para actualizar la aplicación después de hacer cambios:

```bash
# 1. Construir y subir nueva imagen
cd ResQ
gcloud builds submit --tag gcr.io/PROJECT_ID/resq-api:latest

# 2. Desplegar nueva versión
gcloud run deploy resq-api \
    --image gcr.io/PROJECT_ID/resq-api:latest \
    --region us-central1
```

---

## 💰 Estimación de Costos

**Desarrollo/Pruebas (mínimo):**
- Cloud Run: ~$0 (hasta cierto límite de requests)
- Cloud SQL (db-f1-micro): ~$7-10/mes
- Memorystore (1GB basic): ~$30/mes
- **Total aproximado: ~$40-50/mes**

**Producción:**
- Cloud Run: Depende del tráfico
- Cloud SQL (db-n1-standard-1): ~$50-100/mes
- Memorystore (5GB standard): ~$150/mes
- **Total aproximado: ~$200-300/mes** (depende del uso)

---

## 📚 Recursos Adicionales

- [Documentación de Cloud Run](https://cloud.google.com/run/docs)
- [Documentación de Cloud SQL](https://cloud.google.com/sql/docs)
- [Documentación de Memorystore](https://cloud.google.com/memorystore/docs/redis)
- [Precios de Google Cloud](https://cloud.google.com/pricing)

---

**¡Despliegue completado! 🎉**

Si tienes problemas, revisa los logs y la sección de solución de problemas.

