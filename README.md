# ResQ API

API REST desarrollada con FastAPI para el sistema ResQ. Implementa autenticación con JWT, gestión de usuarios/solicitantes, comunicación en tiempo real con WebSockets, y arquitectura en capas.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Tecnologías](#tecnologías)
- [Endpoints Principales](#endpoints-principales)

## ✨ Características

- ✅ Autenticación con JWT (JSON Web Tokens)
- ✅ Hash seguro de contraseñas con bcrypt
- ✅ Arquitectura en capas (API, Security, DataLayer, BusinessLayer)
- ✅ Soporte para PostgreSQL y SQLite
- ✅ Validación de datos con Pydantic
- ✅ Documentación automática con Swagger/OpenAPI
- ✅ Manejo de sesiones de base de datos
- ✅ **Comunicación en tiempo real con WebSockets**
- ✅ **Sistema de notificaciones en tiempo real**
- ✅ **Cache en Redis para ubicaciones de ambulancias**
- ✅ **Integración con LiveKit para llamadas de voz/video**
- ✅ Gestión de usuarios, solicitantes, operadores y ambulancias
- ✅ Gestión de emergencias y solicitudes
- ✅ Tracking de ubicaciones en tiempo real

## 🏗️ Arquitectura

El proyecto sigue una **arquitectura en capas** que separa las responsabilidades:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │  ← Endpoints REST + WebSockets
├─────────────────────────────────────┤
│      Security Layer                 │  ← Autenticación, Hash, JWT
├─────────────────────────────────────┤
│      Business Layer                 │  ← Lógica de negocio, Workflows
│      - Workflows                    │  ← Orquestación de casos de uso
│      - Components                   │  ← Servicios y casos de uso
│      - Notificaciones               │  ← Sistema de notificaciones
│      - Cache                        │  ← Cache en Redis
├─────────────────────────────────────┤
│      Data Layer                     │  ← Acceso a base de datos
└─────────────────────────────────────┘
```

### Flujo de Datos

1. **API Layer**: Recibe las peticiones HTTP/WebSocket y las enruta a los endpoints correspondientes
2. **Security Layer**: Maneja la autenticación, validación de tokens y hash de contraseñas
3. **Business Layer**: Contiene la lógica de negocio (servicios, validaciones, workflows y orquestación)
4. **Data Layer**: Gestiona la conexión a la base de datos y los modelos ORM

## 📁 Estructura del Proyecto

```
ResQ/
├── src/
│   ├── api/                         # Capa de API (Endpoints REST + WebSockets)
│   │   ├── auth.py                  # Endpoints de autenticación
│   │   ├── usuarios.py              # Endpoints de usuarios
│   │   ├── solicitantes.py          # Endpoints de solicitantes
│   │   ├── operadorEmergencia.py    # Endpoints de operadores de emergencia
│   │   ├── operadorAmbulancia.py    # Endpoints de operadores de ambulancia
│   │   ├── ambulancias.py           # Endpoints de ambulancias
│   │   ├── emergencias.py           # Endpoints de emergencias (CRUD)
│   │   ├── evaluarEmergencia.py     # Endpoint para evaluar solicitudes
│   │   ├── solicitudes.py           # Endpoints de solicitudes
│   │   ├── salas.py                 # Endpoints de salas LiveKit
│   │   ├── atenderEmergencias.py    # Endpoints para atender emergencias
│   │   ├── websocketOpEmergencias.py    # WebSocket para operadores
│   │   ├── websocketSolicitantes.py     # WebSocket para solicitantes
│   │   ├── websocketAmbulancias.py      # WebSocket para ambulancias
│   │   ├── recibirNotificaciones.py     # Info de WebSocket solicitantes
│   │   └── infoWebSocketAmbulancias.py  # Info de WebSocket ambulancias
│   │
│   ├── security/                    # Capa de Seguridad
│   │   ├── components/               # Servicios de seguridad
│   │   │   ├── servicioAutenticacion.py  # JWT y autenticación
│   │   │   ├── servicioHash.py           # Hash de contraseñas
│   │   │   └── servicioUsuarios.py       # Gestión de usuarios
│   │   └── entities/                 # Modelos Pydantic
│   │       └── Usuario.py           # Modelo de usuario
│   │
│   ├── businessLayer/                # Capa de Lógica de Negocio
│   │   ├── businessComponents/       # Servicios y casos de uso
│   │   │   ├── entidades/           # Servicios de entidades
│   │   │   ├── notificaciones/      # Sistema de notificaciones
│   │   │   │   ├── notificador.py           # Manager genérico
│   │   │   │   ├── estrategias.py           # Estrategias de notificación
│   │   │   │   ├── notificadorOperadorEmergencias.py
│   │   │   │   └── notificadorSolicitante.py
│   │   │   ├── llamadas/            # Integración LiveKit
│   │   │   └── cache/                # Cache en Redis
│   │   │       ├── configRedis.py
│   │   │       └── servicioUbicacionCache.py
│   │   ├── businessWorkflow/        # Workflows (orquestación)
│   │   │   ├── solicitarAmbulancia.py
│   │   │   ├── evaluarSolicitud.py
│   │   │   ├── procesarUbicacionAmbulancia.py
│   │   │   └── actualizarDisponibilidadAmbulancia.py
│   │   └── businessEntities/        # Entidades y Value Objects (Pydantic)
│   │
│   ├── dataLayer/                    # Capa de Acceso a Datos
│   │   ├── bd.py                    # Configuración de base de datos
│   │   ├── models/                   # Modelos SQLAlchemy
│   │   └── dataAccesComponets/      # Repositorios
│   │
│   └── main.py                      # Punto de entrada de la aplicación
│
├── env/                             # Entorno virtual (no versionado)
├── .env                             # Variables de entorno (no versionado)
├── ENVEXAMPLE                       # Ejemplo de variables de entorno
├── .gitignore
├── requirements.txt                 # Dependencias del proyecto
└── README.md                        # Este archivo
```

## 📦 Requisitos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- PostgreSQL (opcional, puede usar SQLite para desarrollo)
- **Redis** (requerido para cache de ubicaciones en tiempo real)
- **LiveKit** (opcional, para llamadas de voz/video)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd ResQ
```

### 2. Crear entorno virtual

**Windows:**
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Redis

**Con Docker (recomendado):**
```bash
docker run -d -p 6379:6379 --name redis_resq redis:latest
```

**O instalar Redis localmente:**
- Windows: Descargar desde [redis.io](https://redis.io/download)
- Linux: `sudo apt-get install redis-server` (Ubuntu/Debian)
- Mac: `brew install redis`

## ⚙️ Configuración

### Variables de Entorno

1. Copia el archivo de ejemplo:
```bash
cp ENVEXAMPLE .env
```

2. Edita el archivo `.env` con tus configuraciones:

```env
# Base de datos
# Para SQLite (desarrollo):
DATABASE_URL=sqlite:///./resq.db

# Para PostgreSQL (producción):
# DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/resq

# JWT
JWT_SECRET_KEY=tu-clave-secreta-super-segura-y-larga-cambiar-en-produccion
JWT_EXPIRE_MINUTES=1440  # 24 horas

# Redis (Cache en memoria)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# LiveKit (Opcional, para llamadas)
LIVEKIT_API_KEY=tu-api-key
LIVEKIT_API_SECRET=tu-api-secret
LIVEKIT_URL=http://localhost:7880
```

**Nota:** El archivo `ENVEXAMPLE` contiene un template con todas las variables necesarias y sus descripciones.

### Configuración de Base de Datos

#### SQLite (Desarrollo - Por defecto)
No requiere configuración adicional. Se crea automáticamente el archivo `resq.db`.

#### PostgreSQL (Producción)

1. Instalar PostgreSQL
2. Crear la base de datos:
```sql
CREATE DATABASE resq;
```

3. Configurar la URL en `.env`:
```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/resq
```

### Configuración de Redis

Redis se usa para almacenar ubicaciones de ambulancias en tiempo real (sin persistir en disco).

1. **Con Docker (recomendado):**
```bash
docker run -d -p 6379:6379 --name redis_resq redis:latest
```

2. **Verificar que Redis esté funcionando:**
```bash
docker exec redis_resq redis-cli ping
# Debe responder: PONG
```

3. **Configurar en `.env`:**
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

## ▶️ Ejecución

### Modo Desarrollo

```bash
uvicorn src.main:app --reload
```

La aplicación estará disponible en: `http://localhost:8000`

### Modo Producción

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Documentación Interactiva

Una vez ejecutando la aplicación, puedes acceder a:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🧭 Arquitectura y Capas

El proyecto sigue una arquitectura en capas para mantener separación de responsabilidades, escalabilidad y mantenibilidad:

- **API Layer** (`src/api/`): Exposición HTTP (FastAPI), WebSockets, validación inicial y documentación.
- **Security Layer** (`src/security/`): Autenticación JWT, hash de contraseñas y utilidades de seguridad.
- **Business Layer** (`src/businessLayer/`): 
  - **Workflows**: Orquestación de casos de uso complejos
  - **Components**: Servicios de aplicación y casos de uso
  - **Notificaciones**: Sistema de notificaciones en tiempo real con estrategias
  - **Cache**: Gestión de cache en Redis
  - **Entidades**: Modelos de dominio (Pydantic)
- **Data Layer** (`src/dataLayer/`): Modelos ORM (SQLAlchemy), conexión y repositorios de acceso a datos.

Flujo general:
1. La API recibe la solicitud y delega al servicio de negocio o workflow.
2. Los workflows orquestan múltiples servicios y aplican reglas de negocio.
3. Los servicios llaman a repositorios o cache según corresponda.
4. Los repositorios persisten/leen datos mediante SQLAlchemy.
5. El cache (Redis) almacena datos en tiempo real (ubicaciones).
6. La API retorna respuestas tipadas y documentadas.

## 🛠️ Tecnologías

- **FastAPI** 0.121.0 - Framework web moderno y rápido
- **SQLAlchemy** 2.0.44 - ORM para Python
- **Pydantic** 2.12.4 - Validación de datos
- **PyJWT** 2.10.1 - Tokens JWT
- **bcrypt** 5.0.0 - Hash de contraseñas
- **Uvicorn** 0.38.0 - Servidor ASGI
- **python-dotenv** 1.2.1 - Gestión de variables de entorno
- **Redis** 5.0.0+ - Cache en memoria para ubicaciones en tiempo real
- **LiveKit** - Comunicación de voz/video en tiempo real
- **WebSockets** - Comunicación bidireccional en tiempo real

## 📡 Endpoints Principales

### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrar nuevo usuario

### Usuarios
- `GET /usuarios` - Listar usuarios
- `POST /usuarios` - Crear usuario
- `GET /usuarios/{id}` - Obtener usuario

### Solicitudes
- `POST /solicitudes/solicitar-ambulancia` - Crear nueva solicitud
- `GET /solicitudes` - Listar solicitudes

### Emergencias
- `POST /evaluar-emergencia` - Evaluar solicitud y crear emergencia
- `GET /emergencias` - Listar emergencias
- `GET /emergencias/{id}` - Obtener emergencia
- `PUT /emergencias/{id}` - Actualizar emergencia

### WebSockets

#### Operadores de Emergencia
- `WS /ws/operadores-emergencia` - Recibir notificaciones de nuevas solicitudes

#### Solicitantes
- `WS /ws/solicitantes/{id_solicitante}` - Recibir actualizaciones de solicitudes
- `GET /recibir-notificaciones/websocket-info` - Información del WebSocket

#### Ambulancias
- `WS /ws/ambulancias/{id_ambulancia}` - Enviar ubicaciones en tiempo real
- `GET /info-websocket-ambulancias/websocket-info` - Información del WebSocket

### Ambulancias
- `GET /ambulancias` - Listar ambulancias
- `POST /ambulancias` - Crear ambulancia
- `GET /ambulancias/{id}` - Obtener ambulancia
- `PUT /ambulancias/{id}` - Actualizar ambulancia

## 📝 Notas

- Las contraseñas se hashean automáticamente con bcrypt antes de guardarse
- Los tokens JWT tienen una expiración configurable (por defecto 24 horas)
- El proyecto está preparado para escalar con la capa de negocio (businessLayer)
- SQLite se usa por defecto para desarrollo, PostgreSQL para producción
- **Redis almacena solo la última ubicación de cada ambulancia (sin persistir en disco)**
- **Las ubicaciones se actualizan en tiempo real vía WebSocket**
- **El sistema de notificaciones usa el patrón Strategy para diferentes tipos de notificación**

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt (salt único por contraseña)
- ✅ Tokens JWT con expiración
- ✅ Validación de datos con Pydantic
- ✅ Variables sensibles en archivo `.env` (no versionado)
- ✅ CORS configurado para WebSockets
- ✅ Autenticación requerida en la mayoría de endpoints

Autorización en Swagger UI (modo Bearer simple):
- Da clic en "Authorize" y pega: `Bearer <tu_token_jwt>`
- Los endpoints protegidos usarán ese token automáticamente

## 📄 Licencia

[Especificar licencia si aplica]

## 👥 Contribuidores

[Agregar información de contribuidores]

---

**Desarrollado con ❤️ usando FastAPI**
