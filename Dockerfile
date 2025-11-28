# Usar imagen base de Python 3.11
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto que usará la aplicación
# Cloud Run usa la variable de entorno PORT, pero uvicorn usa 8000 por defecto
EXPOSE 8000

# Comando para ejecutar la aplicación
# Cloud Run inyecta la variable PORT, así que la leemos y la usamos
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}


