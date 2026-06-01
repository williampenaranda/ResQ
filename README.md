# ResQ API

API REST desarrollada con FastAPI para el sistema ResQ. Implementa autenticación con JWT, gestión de usuarios/solicitantes, comunicación en tiempo real con WebSockets, y arquitectura en capas.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación y Ejecución](#instalación-y-ejecución)
- [Despliegue en Render](#despliegue-en-render)
- [Tecnologías](#tecnologías)
- [Endpoints Principales](#endpoints-principales)

## ✨ Características

- ✅ Autenticación con JWT (JSON Web Tokens)
- ✅ Hash seguro de contraseñas con bcrypt
- ✅ Arquitectura en capas (API, Security, DataLayer, BusinessLayer)
- ✅ Soporte para PostgreSQL y SQLite
- ✅ Validación de datos con Pydantic
- ✅ Documentación automática con Swagger/OpenAPI
- ✅ Comunicación en tiempo real con WebSockets
- ✅ Sistema de notificaciones en tiempo real
- ✅ Cache en Redis para ubicaciones de ambulancias
- ✅ Integración con LiveKit para llamadas de voz/video
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
│   │   ├── auth.py
│   │   ├── usuarios.py
│   │   ├── solicitantes.py
│   │   ├── operadorEmergencia.py
│   │   ├── operadorAmbulancia.py
│   │   ├── ambulancias.py
│   │   ├── emergencias.py
│   │   ├── solicitudes.py
│   │   ├── salas.py                 # Endpoints de salas LiveKit
│   │   ├── atenderEmergencias.py
│   │   └── websocket*.py            # WebSockets
│   │
│   ├── security/                    # Capa de Seguridad
│   │
│   ├── businessLayer/               # Capa de Lógica de Negocio
│   │   ├── businessComponents/
│   │   │   ├── entidades/
│   │   │   ├── notificaciones/
│   │   │   ├── llamadas/            # Integración LiveKit
│   │   │   └── cache/               # Cache en Redis
│   │   ├── businessWorkflow/
│   │   └── businessEntities/
│   │
│   ├── dataLayer/                   # Capa de Acceso a Datos
│   │   ├── bd.py                    # Configuración de base de datos
│   │   ├── models/                  # Modelos SQLAlchemy
│   │   └── dataAccesComponets/      # Repositorios
│   │
│   └── main.py                      # Punto de entrada de la aplicación
│
├── docker-compose.yml               # PostgreSQL, Redis y LiveKit
├── livekit.yaml                     # Configuración de LiveKit
├── .env                             # Variables de entorno (no versionado)
├── ENVEXAMPLE                       # Ejemplo de variables de entorno
├── requirements.txt                 # Dependencias directas
├── requirements-lock.txt            # Dependencias congeladas
├── DESARROLLO.md                    # Guía de desarrollo local
├── CONFIGURACION_RENDER.md          # Guía de despliegue en Render
└── README.md
```

## 📦 Requisitos

- **Python 3.11+**
- **Docker** (para PostgreSQL, Redis y LiveKit)
- **pip** (gestor de paquetes de Python)

## 🚀 Instalación y Ejecución

Para desarrollo local, sigue la **[Guía de Desarrollo](DESARROLLO.md)**.

Resumen rápido:

```bash
# 1. Clonar
git clone <url-del-repositorio>
cd ResQ

# 2. Entorno virtual y dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-lock.txt

# 3. Iniciar servicios (PostgreSQL + Redis + LiveKit)
docker compose up -d

# 4. Iniciar la app
uvicorn src.main:app --reload

# 5. Abrir http://localhost:8000
```

## ☁️ Despliegue en Render

Consulta la **[Guía de Configuración en Render](CONFIGURACION_RENDER.md)** para las variables de entorno necesarias.

## 🛠️ Tecnologías

- **FastAPI** 0.121.0 - Framework web moderno y rápido
- **SQLAlchemy** 2.0.44 - ORM para Python
- **Pydantic** 2.12.4 - Validación de datos
- **PyJWT** 2.10.1 - Tokens JWT
- **bcrypt** 5.0.0 - Hash de contraseñas
- **Uvicorn** 0.38.0 - Servidor ASGI
- **Redis** 7.1.0 - Cache en memoria para ubicaciones en tiempo real
- **LiveKit** - Comunicación de voz/video en tiempo real
- **WebSockets** - Comunicación bidireccional en tiempo real

## 📡 Endpoints Principales

### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrar nuevo usuario

### Usuarios
- `GET /usuarios` - Listar usuarios
- `POST /usuarios` - Crear usuario

### Solicitudes
- `POST /solicitudes/solicitar-ambulancia` - Crear nueva solicitud

### Emergencias
- `POST /evaluar-emergencia` - Evaluar solicitud y crear emergencia
- `GET /emergencias` - Listar emergencias

### WebSockets
- `WS /ws/operadores-emergencia` - Notificaciones a operadores
- `WS /ws/solicitantes/{id_solicitante}` - Actualizaciones a solicitantes
- `WS /ws/ambulancias/{id_ambulancia}` - Ubicaciones en tiempo real

### Salas (LiveKit)
- `GET /salas/activas` - Listar salas activas
- `PUT /salas` - Unirse a una sala

## 📝 Notas

- La BD por defecto es PostgreSQL vía Docker. Para SQLite, cambiar `DATABASE_URL` en `.env`
- Redis almacena solo la última ubicación de cada ambulancia (sin persistir en disco)
- LiveKit es opcional para llamadas de voz/video; sin él la app arranca igual
- Las contraseñas se hashean automáticamente con bcrypt antes de guardarse
- Los tokens JWT tienen una expiración configurable (por defecto 24 horas)

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt (salt único por contraseña)
- ✅ Tokens JWT con expiración
- ✅ Validación de datos con Pydantic
- ✅ Variables sensibles en archivo `.env` (no versionado)
- ✅ CORS configurado para WebSockets
- ✅ Autenticación requerida en la mayoría de endpoints

## 📄 Licencia

[Especificar licencia si aplica]

## 👥 Contribuidores

[Agregar información de contribuidores]
