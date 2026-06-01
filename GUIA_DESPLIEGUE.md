# Guía de Despliegue - Sistema ResQ

Esta guía explica cómo instalar y ejecutar el sistema ResQ en un servidor Linux.

---

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#1-requisitos-del-sistema)
2. [Instalación de Software Base](#2-instalación-de-software-base)
3. [Instalación del Proyecto](#3-instalación-del-proyecto)
4. [Configuración de Variables de Entorno](#4-configuración-de-variables-de-entorno)
5. [Ejecución del Servidor](#5-ejecución-del-servidor)
6. [Solución de Problemas Comunes](#6-solución-de-problemas-comunes)

---

## 1. Requisitos del Sistema

### Hardware Mínimo Recomendado

- **Procesador**: 2 núcleos mínimo
- **Memoria RAM**: 4 GB mínimo, 8 GB recomendado
- **Espacio en disco**: 5 GB libres

### Software Necesario

1. **Python 3.11 o superior**
2. **Docker** — para PostgreSQL, Redis y LiveKit
3. **Git** — opcional, para clonar el repositorio

---

## 2. Instalación de Software Base

### 2.1 Instalación de Python

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verificar
python3 --version
```

### 2.2 Instalación de Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar para aplicar grupos
```

### 2.3 Instalación de Git (Opcional)

```bash
sudo apt install git
```

---

## 3. Instalación del Proyecto

### 3.1 Obtener el Código

```bash
git clone <url-del-repositorio>
cd ResQ
```

### 3.2 Crear Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

La terminal mostrará `(venv)` al inicio de la línea.

### 3.3 Instalar Dependencias

```bash
pip install -r requirements-lock.txt
```

### 3.4 Iniciar Servicios con Docker

```bash
docker compose up -d
```

Esto inicia:
- **PostgreSQL** (puerto 5432) — base de datos principal
- **Redis** (puerto 6379) — cache de ubicaciones
- **LiveKit** (puertos 7880-7881) — llamadas de voz/video

Verificar que todos estén funcionando:

```bash
docker ps
```

### 3.5 Crear Archivo .env

```bash
cp ENVEXAMPLE .env
```

---

## 4. Configuración de Variables de Entorno

Editar el archivo `.env` con los valores correspondientes:

### Base de Datos (PostgreSQL)

```env
DATABASE_URL=postgresql://resq:resq@localhost:5432/resq
```

### JWT

Generar una clave secreta:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

```env
JWT_SECRET_KEY=clave_generada
JWT_EXPIRE_MINUTES=1440
```

### Redis

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_SSL=false
```

### LiveKit

```env
LIVEKIT_URL=http://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=devsecret
```

---

## 5. Ejecución del Servidor

### Modo Desarrollo

```bash
uvicorn src.main:app --reload
```

### Modo Producción

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Detener con `CTRL + C`.

---

## 6. Solución de Problemas Comunes

### Error: "No se puede conectar a la base de datos"

1. Verificar que PostgreSQL esté corriendo: `docker ps | grep postgres`
2. Verificar las credenciales en `.env`

### Error: "Redis connection refused"

1. Verificar que Redis esté corriendo: `docker ps | grep redis`
2. Verificar puerto en `.env`

### Error: "ModuleNotFoundError"

1. Asegurarse de que el entorno virtual esté activo (`(venv)` visible)
2. Reinstalar dependencias: `pip install -r requirements-lock.txt`

### Error: "Port 8000 already in use"

```bash
uvicorn src.main:app --reload --port 8001
```

### Error: "LIVEKIT_API_KEY no está configurada"

LiveKit es opcional. Si no se necesita, ignorar el mensaje. Para usarlo, configurar las variables `LIVEKIT_*` en `.env`.

---

## ✅ Verificación Final

1. ✅ El servidor inicia sin errores
2. ✅ http://localhost:8000/docs carga correctamente
3. ✅ No hay errores en la terminal

---

## ☁️ Despliegue en Render

Para desplegar en Render, consultar la **[Guía de Configuración en Render](CONFIGURACION_RENDER.md)**.

---

**Instalación del sistema ResQ completada.**
