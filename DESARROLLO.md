# Guía de Desarrollo — ResQ API

## Requisitos

- Python 3.11+
- Docker

## Setup inicial

```bash
# 1. Clonar e ir al directorio
cd ResQ

# 2. Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-lock.txt

# 3. Iniciar PostgreSQL + Redis + LiveKit
docker compose up -d

# 4. Iniciar la app
uvicorn src.main:app --reload

# 5. Abrir http://localhost:8000
```

## Comandos diarios

```bash
source venv/bin/activate                    # activar entorno
docker compose up -d                         # iniciar servicios
docker compose logs -f                       # ver logs de servicios
docker compose down                          # detener servicios
uvicorn src.main:app --reload                # iniciar app en modo desarrollo
```

## Servicios

| Servicio    | Puerto | URL                                        |
|-------------|--------|--------------------------------------------|
| App         | 8000   | http://localhost:8000                      |
| PostgreSQL  | 5432   | `postgresql://resq:resq@localhost:5432/resq` |
| Redis       | 6379   | `redis://localhost:6379`                   |
| LiveKit     | 7880   | http://localhost:7880                      |
| LiveKit TCP | 7881   | `localhost:7881`                           |

## Endpoints principales

- `GET /` — estado de la API
- `GET /health` — health check
- `GET /docs` — Swagger UI (FastAPI)
- `GET /salas/activas` — salas de LiveKit activas

## Variables de entorno (`.env`)

| Variable            | Descripción          | Default dev                               |
|---------------------|----------------------|-------------------------------------------|
| `DATABASE_URL`      | Conexión BD          | `postgresql://resq:resq@localhost:5432/resq` |
| `JWT_SECRET_KEY`    | Clave JWT            | preconfigurada                             |
| `REDIS_HOST`        | Host Redis           | `localhost`                                |
| `REDIS_PORT`        | Puerto Redis         | `6379`                                     |
| `LIVEKIT_URL`       | URL LiveKit          | `http://localhost:7880`                    |
| `LIVEKIT_API_KEY`   | Key LiveKit          | `devkey`                                   |
| `LIVEKIT_API_SECRET`| Secret LiveKit       | `devsecret`                                |

## Dependencias

- `requirements.txt` — dependencias directas con versiones fijas
- `requirements-lock.txt` — todas las dependencias (directas + transitivas) congeladas con `pip freeze`

Para añadir una dependencia:

```bash
pip install <paquete>
pip freeze > requirements-lock.txt
# y agregarlo también a requirements.txt
```

## Notas

- La BD por defecto es PostgreSQL vía Docker. Para SQLite, cambiar `DATABASE_URL` en `.env`
- Redis se usa para cache de ubicaciones de ambulancias (no persistente)
- LiveKit es opcional para llamadas de voz/video; sin él la app arranca igual
