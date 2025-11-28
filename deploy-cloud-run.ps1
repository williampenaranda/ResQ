# Script de PowerShell para desplegar ResQ en Google Cloud Run
# Uso: .\deploy-cloud-run.ps1

param(
    [string]$Region = "us-central1",
    [string]$ServiceName = "resq-api",
    [string]$CloudSqlInstance = "resq-postgres",
    [string]$RedisInstance = "resq-redis"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Script de Despliegue de ResQ en Google Cloud Run" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que gcloud está instalado
try {
    $null = gcloud --version 2>&1
} catch {
    Write-Host "❌ Error: gcloud no está instalado" -ForegroundColor Red
    Write-Host "Instala Google Cloud SDK desde: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Obtener proyecto actual
$ProjectId = gcloud config get-value project 2>$null
if (-not $ProjectId) {
    Write-Host "❌ Error: No hay un proyecto configurado" -ForegroundColor Red
    Write-Host "Ejecuta: gcloud config set project PROJECT_ID" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Proyecto: $ProjectId" -ForegroundColor Green
Write-Host ""
Write-Host "Configuración:" -ForegroundColor Cyan
Write-Host "  - Región: $Region"
Write-Host "  - Servicio: $ServiceName"
Write-Host "  - Cloud SQL: $CloudSqlInstance"
Write-Host "  - Redis: $RedisInstance"
Write-Host ""

# Función para construir y subir imagen
function Build-AndPush {
    Write-Host "📦 Construyendo y subiendo imagen Docker..." -ForegroundColor Yellow
    gcloud builds submit --tag "gcr.io/$ProjectId/$ServiceName`:latest"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Imagen construida y subida" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al construir imagen" -ForegroundColor Red
        exit 1
    }
}

# Función para desplegar en Cloud Run
function Deploy-Service {
    Write-Host "🚀 Desplegando servicio en Cloud Run..." -ForegroundColor Yellow
    
    $CloudSqlConnection = "$ProjectId`:$Region`:$CloudSqlInstance"
    
    gcloud run deploy $ServiceName `
        --image "gcr.io/$ProjectId/$ServiceName`:latest" `
        --platform managed `
        --region $Region `
        --allow-unauthenticated `
        --memory 512Mi `
        --cpu 1 `
        --timeout 300 `
        --max-instances 10 `
        --min-instances 0 `
        --add-cloudsql-instances=$CloudSqlConnection
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Servicio desplegado" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al desplegar servicio" -ForegroundColor Red
        exit 1
    }
}

# Función para obtener información de Cloud SQL
function Get-CloudSqlInfo {
    Write-Host "📊 Obteniendo información de Cloud SQL..." -ForegroundColor Yellow
    
    try {
        $null = gcloud sql instances describe $CloudSqlInstance 2>&1
        Write-Host "✓ Cloud SQL encontrado" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Error: La instancia de Cloud SQL '$CloudSqlInstance' no existe" -ForegroundColor Red
        Write-Host "Créala primero con: gcloud sql instances create $CloudSqlInstance ..." -ForegroundColor Yellow
        return $false
    }
}

# Función para obtener información de Redis
function Get-RedisInfo {
    Write-Host "📊 Obteniendo información de Redis..." -ForegroundColor Yellow
    
    try {
        $RedisInfo = gcloud redis instances describe $RedisInstance --region=$Region 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Error: La instancia de Redis '$RedisInstance' no existe" -ForegroundColor Red
            Write-Host "Créala primero con: gcloud redis instances create $RedisInstance ..." -ForegroundColor Yellow
            return $false
        }
        
        $RedisHost = gcloud redis instances describe $RedisInstance --region=$Region --format="value(host)"
        Write-Host "Redis Host: $RedisHost" -ForegroundColor Cyan
        Write-Host "✓ Redis encontrado" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Error al obtener información de Redis" -ForegroundColor Red
        return $false
    }
}

# Función para configurar variables de entorno
function Configure-EnvVars {
    Write-Host "⚙️  Configurando variables de entorno..." -ForegroundColor Yellow
    
    $CloudSqlConnection = "$ProjectId`:$Region`:$CloudSqlInstance"
    $RedisHost = gcloud redis instances describe $RedisInstance --region=$Region --format="value(host)"
    
    # Solicitar valores al usuario
    $DbUser = Read-Host "Usuario de la base de datos (app_user)"
    if ([string]::IsNullOrWhiteSpace($DbUser)) {
        $DbUser = "app_user"
    }
    
    $DbPassword = Read-Host "Contraseña de la base de datos" -AsSecureString
    $DbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($DbPassword)
    )
    
    $DbName = Read-Host "Nombre de la base de datos (resq)"
    if ([string]::IsNullOrWhiteSpace($DbName)) {
        $DbName = "resq"
    }
    
    $JwtSecret = Read-Host "JWT Secret Key (dejar vacío para generar)"
    if ([string]::IsNullOrWhiteSpace($JwtSecret)) {
        # Generar clave secreta
        $JwtSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
        Write-Host "JWT Secret generado: $JwtSecret" -ForegroundColor Cyan
    }
    
    # Construir DATABASE_URL para Cloud SQL (socket Unix)
    $DatabaseUrl = "postgresql://${DbUser}:${DbPasswordPlain}@/${DbName}?host=/cloudsql/${CloudSqlConnection}"
    
    Write-Host ""
    Write-Host "Configurando variables de entorno..." -ForegroundColor Yellow
    
    gcloud run services update $ServiceName `
        --region=$Region `
        --update-env-vars="DATABASE_URL=$DatabaseUrl" `
        --update-env-vars="JWT_SECRET_KEY=$JwtSecret" `
        --update-env-vars="JWT_EXPIRE_MINUTES=1440" `
        --update-env-vars="REDIS_HOST=$RedisHost" `
        --update-env-vars="REDIS_PORT=6379" `
        --update-env-vars="REDIS_PASSWORD=" `
        --update-env-vars="REDIS_DB=0"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Variables de entorno configuradas" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al configurar variables de entorno" -ForegroundColor Red
        exit 1
    }
}

# Función para mostrar información del servicio
function Show-ServiceInfo {
    Write-Host ""
    Write-Host "📋 Información del Servicio:" -ForegroundColor Yellow
    Write-Host "==================================" -ForegroundColor Yellow
    
    $ServiceUrl = gcloud run services describe $ServiceName --region=$Region --format="value(status.url)"
    Write-Host "URL: $ServiceUrl" -ForegroundColor Cyan
    Write-Host "Health Check: $ServiceUrl/health" -ForegroundColor Cyan
    Write-Host "Documentación: $ServiceUrl/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Para ver logs:" -ForegroundColor Yellow
    Write-Host "  gcloud run services logs read $ServiceName --region=$Region --follow" -ForegroundColor Gray
}

# Menú principal
Write-Host "¿Qué deseas hacer?" -ForegroundColor Cyan
Write-Host "1) Construir y subir imagen Docker"
Write-Host "2) Desplegar servicio en Cloud Run"
Write-Host "3) Configurar variables de entorno"
Write-Host "4) Hacer todo (build + deploy + config)"
Write-Host "5) Ver información del servicio"
Write-Host "6) Ver logs"
Write-Host ""
$Option = Read-Host "Selecciona una opción (1-6)"

switch ($Option) {
    "1" {
        Build-AndPush
    }
    "2" {
        if (-not (Get-CloudSqlInfo)) { exit 1 }
        Deploy-Service
    }
    "3" {
        if (-not (Get-CloudSqlInfo)) { exit 1 }
        if (-not (Get-RedisInfo)) { exit 1 }
        Configure-EnvVars
    }
    "4" {
        if (-not (Get-CloudSqlInfo)) { exit 1 }
        if (-not (Get-RedisInfo)) { exit 1 }
        Build-AndPush
        Deploy-Service
        Configure-EnvVars
        Show-ServiceInfo
    }
    "5" {
        Show-ServiceInfo
    }
    "6" {
        Write-Host "📜 Mostrando logs (Ctrl+C para salir)..." -ForegroundColor Yellow
        gcloud run services logs read $ServiceName --region=$Region --follow
    }
    default {
        Write-Host "❌ Opción inválida" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "✅ Completado" -ForegroundColor Green


