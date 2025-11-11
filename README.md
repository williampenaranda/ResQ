# ResQ API

API REST desarrollada con FastAPI para el sistema ResQ. Implementa autenticación con JWT, gestión de usuarios/solicitantes y arquitectura en capas.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Endpoints](#endpoints)
- [Tecnologías](#tecnologías)

## ✨ Características

- ✅ Autenticación con JWT (JSON Web Tokens)
- ✅ Hash seguro de contraseñas con bcrypt
- ✅ Arquitectura en capas (API, Security, DataLayer, BusinessLayer)
- ✅ Soporte para PostgreSQL y SQLite
- ✅ Validación de datos con Pydantic
- ✅ Documentación automática con Swagger/OpenAPI
- ✅ Manejo de sesiones de base de datos
- ✅ Gestión de usuarios
- ✅ Gestión de solicitantes

## 🏗️ Arquitectura

El proyecto sigue una **arquitectura en capas** que separa las responsabilidades:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │  ← Endpoints REST
├─────────────────────────────────────┤
│      Security Layer                 │  ← Autenticación, Hash, JWT
├─────────────────────────────────────┤
│      Business Layer                 │  ← Lógica de negocio
├─────────────────────────────────────┤
│      Data Layer                     │  ← Acceso a base de datos
└─────────────────────────────────────┘
```

### Flujo de Datos

1. **API Layer**: Recibe las peticiones HTTP y las enruta a los endpoints correspondientes
2. **Security Layer**: Maneja la autenticación, validación de tokens y hash de contraseñas
3. **Business Layer**: Contiene la lógica de negocio (servicios, validaciones y orquestación)
4. **Data Layer**: Gestiona la conexión a la base de datos y los modelos ORM

## 📁 Estructura del Proyecto

```
ResQ/
├── src/
│   ├── api/                    # Capa de API (Endpoints REST)
│   │   ├── auth.py            # Endpoints de autenticación
│   │   ├── usuarios.py        # Endpoints de usuarios
│   │   └── solicitantes.py    # Endpoints de solicitantes
│   │
│   ├── security/              # Capa de Seguridad
│   │   ├── components/        # Servicios de seguridad
│   │   │   ├── servicioAutenticacion.py  # JWT y autenticación
│   │   │   ├── servicioHash.py           # Hash de contraseñas
│   │   │   └── servicioUsuarios.py       # Gestión de usuarios
│   │   └── entities/          # Modelos Pydantic
│   │       ├── Usuario.py     # Modelo de usuario
│   │       └── LoginRequest.py # Modelos de autenticación
│   │
│   ├── businessLayer/         # Capa de Lógica de Negocio
│   │   ├── businessComponents/ # Servicios de aplicación (casos de uso)
│   │   └── businessEntities/   # Entidades y Value Objects (Pydantic)
│   │
│   ├── dataLayer/             # Capa de Acceso a Datos
│   │   ├── bd.py             # Configuración de base de datos
│   │   └── models/           # Modelos SQLAlchemy
│   │       ├── modeloUsuario.py
│   │       └── modeloSolicitante.py
│   │
│   └── main.py               # Punto de entrada de la aplicación
│
├── env/                      # Entorno virtual (no versionado)
├── .env                      # Variables de entorno (no versionado)
├── .env.example             # Ejemplo de variables de entorno
├── .gitignore
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Este archivo
```

## 📦 Requisitos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- PostgreSQL (opcional, puede usar SQLite para desarrollo)

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

## ⚙️ Configuración

### Variables de Entorno

1. Copia el archivo de ejemplo:
```bash
cp .env.example .env
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
```

**Nota:** El archivo `.env.example` contiene un template con todas las variables necesarias y sus descripciones.

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

## 🔌 Endpoints

### Autenticación

#### `POST /auth/login`
Autentica un usuario y devuelve un token JWT.

**Request:**
```json
{
  "identificador": "usuario@email.com",  // o "nombreDeUsuario"
  "contrasena": "mi_contraseña"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### `POST /auth/verify`
Verifica si un token JWT es válido.

**Request:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (válido):**
```json
{
  "valid": true,
  "usuario": {
    "nombreDeUsuario": "usuario123",
    "email": "usuario@email.com",
    "sub": "usuario@email.com"
  },
  "mensaje": "Token válido"
}
```

### Usuarios

#### `POST /usuarios/`
Crea un nuevo usuario.

**Request:**
```json
{
  "nombreDeUsuario": "usuario123",
  "email": "usuario@email.com",
  "contrasenaHasheada": "contraseña_sin_hashear"
}
```

**Response:**
```json
{
  "mensaje": "Usuario creado correctamente"
}
```

### Solicitantes

#### `POST /solicitantes`
Crea un nuevo solicitante.

Ejemplo de cuerpo (resumen, ver schema en Swagger):
```json
{
  "nombre": "Juan",
  "apellido": "Pérez",
  "fechaNacimiento": "1990-05-10",
  "tipoDocumento": "CEDULA",
  "numeroDocumento": "1234567890",
  "padecimientos": ["hipertensión"]
}
```

Respuesta (201):
```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Pérez",
  "fechaNacimiento": "1990-05-10",
  "tipoDocumento": "CEDULA",
  "numeroDocumento": "1234567890",
  "padecimientos": ["hipertensión"]
}
```

#### `GET /solicitantes/{id}`
Retorna un solicitante por ID.

#### `PUT /solicitantes/{id}`
Actualiza campos y retorna el solicitante actualizado.

#### `DELETE /solicitantes/{id}`
Elimina un solicitante (204 No Content).

### Health Check

#### `GET /`
Endpoint raíz para verificar que la API está funcionando.

#### `GET /health`
Endpoint de health check.

## 🛠️ Tecnologías

- **FastAPI** 0.121.0 - Framework web moderno y rápido
- **SQLAlchemy** 2.0.44 - ORM para Python
- **Pydantic** 2.12.4 - Validación de datos
- **PyJWT** 2.10.1 - Tokens JWT
- **bcrypt** 5.0.0 - Hash de contraseñas
- **Uvicorn** 0.38.0 - Servidor ASGI
- **python-dotenv** 1.2.1 - Gestión de variables de entorno

## 📝 Notas

- Las contraseñas se hashean automáticamente con bcrypt antes de guardarse
- Los tokens JWT tienen una expiración configurable (por defecto 24 horas)
- El proyecto está preparado para escalar con la capa de negocio (businessLayer)
- SQLite se usa por defecto para desarrollo, PostgreSQL para producción

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt (salt único por contraseña)
- ✅ Tokens JWT con expiración
- ✅ Validación de datos con Pydantic
- ✅ Variables sensibles en archivo `.env` (no versionado)

Autorización en Swagger UI (modo Bearer simple):
- Da clic en “Authorize” y pega: `Bearer <tu_token_jwt>`
- Los endpoints protegidos usarán ese token automáticamente

## 📄 Licencia

[Especificar licencia si aplica]

## 👥 Contribuidores

[Agregar información de contribuidores]

---

**Desarrollado con ❤️ usando FastAPI**

