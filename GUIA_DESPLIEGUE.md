# Guía de Despliegue - Sistema ResQ

Esta guía explica el procedimiento para instalar y configurar el sistema ResQ paso a paso, asumiendo que el código del proyecto ya está disponible en el equipo.

---

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#1-requisitos-del-sistema)
2. [Instalación de Software Base](#2-instalación-de-software-base)
3. [Instalación del Proyecto](#3-instalación-del-proyecto)
4. [Configuración de Base de Datos](#4-configuración-de-base-de-datos)
5. [Configuración de Redis](#5-configuración-de-redis)
6. [Configuración de Variables de Entorno](#6-configuración-de-variables-de-entorno)
7. [Inicialización de la Base de Datos](#7-inicialización-de-la-base-de-datos)
8. [Ejecución del Servidor](#8-ejecución-del-servidor)
9. [Solución de Problemas Comunes](#9-solución-de-problemas-comunes)

---

## 1. Requisitos del Sistema

### Hardware Mínimo Recomendado

- **Procesador**: Intel Core i3 o equivalente (2 núcleos mínimo)
- **Memoria RAM**: 4 GB mínimo, 8 GB recomendado
- **Espacio en disco**: 5 GB libres
- **Conexión a Internet**: Para descargar software y dependencias

### Software Necesario

Se requiere instalar los siguientes programas antes de comenzar:

1. **Python 3.11 o superior** - Lenguaje de programación
2. **PostgreSQL 12 o superior** - Base de datos (o SQLite para desarrollo)
3. **Redis** - Sistema de caché en memoria
4. **Git** - Opcional, solo si se necesita descargar código adicional

**Nota**: Si se prefiere no instalar PostgreSQL y Redis manualmente, se puede usar Docker (se explica más adelante).

---

## 2. Instalación de Software Base

### 2.1 Instalación de Python

Python es el lenguaje de programación utilizado por este sistema. Se requiere la versión 3.11 o superior.

#### Windows

1. Acceder a la página oficial de Python: https://www.python.org/downloads/
2. Descargar la versión más reciente de Python 3.11 o superior
3. Ejecutar el instalador descargado
4. **IMPORTANTE**: Marcar la casilla "Add Python to PATH" antes de hacer clic en "Install Now"
5. Hacer clic en "Install Now" y esperar a que termine la instalación
6. Verificar la instalación abriendo la terminal (PowerShell o CMD) y ejecutando:
   ```powershell
   python --version
   ```
   Debe mostrarse algo como: `Python 3.11.x` o superior

#### Linux (Ubuntu/Debian)

1. Abrir una terminal
2. Actualizar la lista de paquetes:
   ```bash
   sudo apt update
   ```
3. Instalar Python y pip:
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```
4. Verificar la instalación:
   ```bash
   python3 --version
   ```
   Debe mostrarse: `Python 3.11.x` o superior

#### Mac

1. Abrir la aplicación "Terminal"
2. Instalar Homebrew si no está instalado (copiar y pegar este comando):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Instalar Python:
   ```bash
   brew install python3
   ```
4. Verificar la instalación:
   ```bash
   python3 --version
   ```

### 2.2 Instalación de PostgreSQL

PostgreSQL es la base de datos que almacenará toda la información del sistema.

#### Windows

1. Acceder a: https://www.postgresql.org/download/windows/
2. Descargar el instalador de PostgreSQL (elegir la versión más reciente)
3. Ejecutar el instalador
4. Durante la instalación:
   - Elegir un puerto (dejar el predeterminado 5432)
   - **Anotar la contraseña del usuario "postgres"** - se necesitará más adelante
   - Completar la instalación
5. PostgreSQL se instalará como un servicio de Windows y se iniciará automáticamente

#### Linux (Ubuntu/Debian)

1. Abrir una terminal
2. Instalar PostgreSQL:
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```
3. Iniciar el servicio:
   ```bash
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```
4. Configurar la contraseña del usuario postgres:
   ```bash
   sudo -u postgres psql
   ```
   Luego en la consola de PostgreSQL, escribir:
   ```sql
   ALTER USER postgres PASSWORD 'contraseña_segura';
   \q
   ```
   (Reemplazar `contraseña_segura` con una contraseña elegida)

#### Mac

1. Abrir Terminal
2. Instalar PostgreSQL con Homebrew:
   ```bash
   brew install postgresql@14
   ```
3. Iniciar el servicio:
   ```bash
   brew services start postgresql@14
   ```
4. Crear un usuario y base de datos:
   ```bash
   createuser -s postgres
   ```

### 2.3 Instalación de Redis

Redis es un sistema de caché en memoria que se usa para almacenar ubicaciones de ambulancias en tiempo real.

#### Opción A: Usando Docker (Recomendado - Más Fácil)

Docker es una herramienta que permite ejecutar aplicaciones en contenedores sin instalar todo el software manualmente.

**Instalación de Docker:**

- **Windows/Mac**: Descargar Docker Desktop desde https://www.docker.com/products/docker-desktop
- **Linux**: 
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  ```

**Una vez instalado Docker, ejecutar Redis:**

```bash
docker run -d -p 6379:6379 --name redis_resq redis:latest
```

Este comando descarga e inicia Redis automáticamente. Verificar que esté funcionando:

```bash
docker ps
```

Debe mostrarse un contenedor llamado "redis_resq" en ejecución.

#### Opción B: Instalación Local (Sin Docker)

**Windows:**

1. Descargar Redis desde: https://github.com/microsoftarchive/redis/releases
2. Descargar el archivo `.msi` más reciente
3. Ejecutar el instalador
4. Redis se instalará como servicio de Windows

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Mac:**

```bash
brew install redis
brew services start redis
```

**Verificar que Redis funciona:**

Abrir una terminal y ejecutar:

```bash
redis-cli ping
```

Si responde `PONG`, Redis está funcionando correctamente.

### 2.4 Instalación de Git (Opcional)

Git se usa para gestionar versiones del código. Si el código ya está disponible, se puede omitir este paso.

**Windows:** Descargar desde https://git-scm.com/download/win

**Linux:**
```bash
sudo apt install git
```

**Mac:**
```bash
brew install git
```

---

## 3. Instalación del Proyecto

### 3.1 Navegar a la Carpeta del Proyecto

Abrir una terminal y navegar a la carpeta donde se encuentra el código del proyecto:

```bash
cd ruta/al/proyecto/ResQ
```

### 3.2 Crear Entorno Virtual

Un entorno virtual es un espacio aislado donde se instalan las dependencias del proyecto sin afectar otros programas de Python en el equipo.

**Windows (PowerShell):**
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

Si se obtiene un error de permisos en PowerShell, ejecutar primero:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (CMD):**
```cmd
python -m venv env
env\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv env
source env/bin/activate
```

**Indicador de entorno virtual activo:**

Se verá `(env)` al inicio de la línea de comandos, así:
```
(env) C:\Users\Usuario\ResQ>
```

### 3.3 Instalar Dependencias del Proyecto

Con el entorno virtual activo, instalar todas las librerías necesarias:

```bash
pip install -r requirements.txt
```

Este proceso puede tardar varios minutos. Esperar a que termine completamente.

**Nota**: Si se está en Linux o Mac y se obtienen errores de permisos, usar `pip3` en lugar de `pip`.

---

## 4. Configuración de Base de Datos

### 4.1 Crear Base de Datos en PostgreSQL

Se debe crear una base de datos donde se almacenará toda la información del sistema.

**Windows:**

1. Abrir "pgAdmin" (se instala con PostgreSQL) o usar la terminal
2. Si se usa la terminal, abrir PowerShell o CMD y ejecutar:
   ```powershell
   psql -U postgres
   ```
   (Solicitará la contraseña configurada durante la instalación)

**Linux/Mac:**

Abrir una terminal y ejecutar:
```bash
sudo -u postgres psql
```

**Una vez dentro de PostgreSQL, ejecutar estos comandos:**

```sql
CREATE DATABASE resq;
\q
```

Esto crea una base de datos llamada "resq". Presionar Enter después de cada comando.

### 4.2 Verificar la Conexión

Para verificar que se puede conectar a la base de datos:

```bash
psql -U postgres -d resq
```

Si se puede entrar sin errores, la base de datos está lista.

**Alternativa para Desarrollo: SQLite**

Si se prefiere no usar PostgreSQL (más simple pero menos potente), se puede usar SQLite que no requiere instalación adicional. Solo se necesitará configurar la variable de entorno más adelante.

---

## 5. Configuración de Redis

### 5.1 Verificar que Redis Está Funcionando

Abrir una terminal y ejecutar:

```bash
redis-cli ping
```

**Si se usa Docker:**
```bash
docker exec redis_resq redis-cli ping
```

Debe recibirse la respuesta `PONG`. Si se obtiene un error, revisar la sección de solución de problemas.

### 5.2 Configuración de Redis (Si es Necesaria)

Por defecto, Redis funciona en:
- **Host**: localhost
- **Puerto**: 6379
- **Contraseña**: ninguna (por defecto)

Si se cambió la configuración de Redis, anotar los valores porque se necesitarán más adelante.

---

## 6. Configuración de Variables de Entorno

Las variables de entorno son configuraciones que el sistema necesita para funcionar, como la dirección de la base de datos y claves secretas.

### 6.1 Crear Archivo .env

1. En la carpeta del proyecto, buscar el archivo llamado `ENVEXAMPLE`
2. Copiarlo y renombrarlo a `.env` (sin extensión, solo punto env)

**Windows:**
```powershell
Copy-Item ENVEXAMPLE .env
```

**Linux/Mac:**
```bash
cp ENVEXAMPLE .env
```

### 6.2 Editar el Archivo .env

Abrir el archivo `.env` con un editor de texto (Bloc de notas, Notepad++, VS Code, etc.) y configurar los siguientes valores:

#### Configuración de Base de Datos

**Para PostgreSQL:**
```env
DATABASE_URL=postgresql://postgres:contraseña@localhost:5432/resq
```

Reemplazar `contraseña` con la contraseña configurada para el usuario postgres.

**Para SQLite (más simple, solo para desarrollo):**
```env
DATABASE_URL=sqlite:///./resq.db
```

#### Configuración de JWT (Autenticación)

Se debe generar una clave secreta segura. Abrir una terminal (con el entorno virtual activo) y ejecutar:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copiar el texto que aparece y usarlo en el archivo `.env`:

```env
JWT_SECRET_KEY=clave_generada_aquí
JWT_EXPIRE_MINUTES=1440
```

**Importante**: La clave secreta debe ser diferente en producción y mantenerse en secreto.

#### Configuración de Redis

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

Si se configuró Redis con contraseña, ponerla en `REDIS_PASSWORD`. Si no, dejarlo vacío.

#### Configuración de LiveKit (Opcional)

LiveKit se usa para llamadas de voz/video. Si no se va a usar, se pueden dejar estas líneas comentadas o con valores vacíos:

```env
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
LIVEKIT_URL=
```

Si se tiene una cuenta de LiveKit, completar estos valores con las credenciales correspondientes.

### 6.3 Ejemplo Completo de Archivo .env

```env
# Base de datos
DATABASE_URL=postgresql://postgres:contraseña_segura@localhost:5432/resq

# JWT
JWT_SECRET_KEY=clave_secreta_generada_con_el_comando_python
JWT_EXPIRE_MINUTES=1440

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# LiveKit (Opcional)
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
LIVEKIT_URL=
```

---

## 7. Inicialización de la Base de Datos

El sistema creará automáticamente todas las tablas necesarias la primera vez que se ejecute. Sin embargo, se puede verificar que todo esté configurado correctamente.

### 7.1 Verificar la Configuración

Asegurarse de que:
1. El archivo `.env` está en la carpeta del proyecto
2. PostgreSQL está ejecutándose
3. Redis está ejecutándose
4. El entorno virtual está activo

### 7.2 Probar la Conexión

Se puede probar que todo funciona ejecutando un comando de Python:

```bash
python -c "from src.dataLayer.bd import engine; print('Conexión exitosa!')"
```

Si no se obtienen errores, la configuración está correcta.

---

## 8. Ejecución del Servidor

### 8.1 Modo Desarrollo

El modo desarrollo es útil para probar y desarrollar. El servidor se reinicia automáticamente cuando se hacen cambios en el código.

Asegurarse de que:
- El entorno virtual está activo (se ve `(env)` en la terminal)
- Se está en la carpeta del proyecto

**Ejecutar:**

```bash
uvicorn src.main:app --reload
```

Debe mostrarse un mensaje como:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**El servidor está funcionando.**

### 8.2 Acceder a la Aplicación

Abrir el navegador web y acceder a:

- **API Principal**: http://localhost:8000
- **Documentación Interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación Alternativa (ReDoc)**: http://localhost:8000/redoc

### 8.3 Modo Producción

Para ejecutar el servidor en modo producción (más estable, sin reinicio automático):

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Nota**: En producción, se recomienda usar un servidor WSGI como Gunicorn con múltiples workers para mejor rendimiento.

### 8.4 Detener el Servidor

Para detener el servidor, presionar `CTRL + C` en la terminal donde está ejecutándose.

---

## 9. Solución de Problemas Comunes

### Error: "No se puede conectar a la base de datos"

**Posibles causas y soluciones:**

1. **PostgreSQL no está ejecutándose**
   - **Windows**: Abrir "Servicios" (services.msc) y buscar "postgresql", iniciarlo si está detenido
   - **Linux**: `sudo systemctl start postgresql`
   - **Mac**: `brew services start postgresql@14`

2. **Contraseña incorrecta en DATABASE_URL**
   - Verificar que la contraseña en el archivo `.env` sea correcta
   - Probar conectarse manualmente: `psql -U postgres`

3. **Base de datos no existe**
   - Crear la base de datos: `CREATE DATABASE resq;` (ver sección 4.1)

4. **Puerto incorrecto**
   - Verificar que PostgreSQL esté en el puerto 5432 (por defecto)
   - Si se usa otro puerto, actualizar `DATABASE_URL` en `.env`

### Error: "Redis connection refused" o "Redis no disponible"

**Soluciones:**

1. **Redis no está ejecutándose**
   - **Con Docker**: `docker start redis_resq`
   - **Sin Docker**: 
     - Windows: Iniciar el servicio Redis desde "Servicios"
     - Linux: `sudo systemctl start redis-server`
     - Mac: `brew services start redis`

2. **Puerto incorrecto**
   - Verificar que Redis esté en el puerto 6379
   - Probar: `redis-cli ping` (debe responder PONG)

3. **Redis con contraseña**
   - Si se configuró Redis con contraseña, agregar `REDIS_PASSWORD=contraseña` en `.env`

### Error: "ModuleNotFoundError" o "No module named..."

**Solución:**

1. Asegurarse de que el entorno virtual está activo (debe verse `(env)` en la terminal)
2. Reinstalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Error: "Port 8000 already in use"

**Solución:**

Otra aplicación está usando el puerto 8000. Existen dos opciones:

1. **Detener la otra aplicación** que usa el puerto
2. **Usar otro puerto**:
   ```bash
   uvicorn src.main:app --reload --port 8001
   ```
   Luego acceder a http://localhost:8001

### Error: "Permission denied" en Linux/Mac

**Solución:**

Algunos comandos requieren permisos de administrador. Usar `sudo` cuando sea necesario:

```bash
sudo systemctl start postgresql
sudo systemctl start redis-server
```

### Error al activar entorno virtual en Windows PowerShell

**Solución:**

Ejecutar este comando una vez:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Luego intentar activar el entorno virtual nuevamente.

### El servidor inicia pero no se puede acceder desde otro equipo

**Solución:**

En modo desarrollo, el servidor solo acepta conexiones locales. Para permitir conexiones externas, usar:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Advertencia**: Solo hacer esto en redes de confianza. En producción, usar un servidor web (nginx) como proxy reverso.

### Error: "JWT_SECRET_KEY not set"

**Solución:**

Asegurarse de que el archivo `.env` existe y contiene `JWT_SECRET_KEY` con un valor. Generar una nueva clave si es necesario (ver sección 6.2).

---

## ✅ Verificación Final

Para verificar que todo está funcionando correctamente:

1. ✅ El servidor inicia sin errores
2. ✅ Se puede acceder a http://localhost:8000/docs
3. ✅ La página de documentación se carga correctamente
4. ✅ No hay errores en la terminal del servidor

Si todos estos puntos se cumplen, **la instalación está completa y funcionando.**

---

## 📞 Soporte Adicional

Si se encuentran problemas que no están cubiertos en esta guía:

1. Revisar los mensajes de error en la terminal - suelen indicar qué está mal
2. Verificar que todos los servicios (PostgreSQL, Redis) estén ejecutándose
3. Asegurarse de que el archivo `.env` está configurado correctamente
4. Revisar los logs del servidor para más detalles

---

**Instalación del sistema ResQ completada.**
