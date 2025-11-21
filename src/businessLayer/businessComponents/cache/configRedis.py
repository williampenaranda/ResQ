"""
Módulo de configuración compartida para Redis.
Centraliza la carga y validación de las variables de entorno de Redis.
"""

import os
from dotenv import load_dotenv
from typing import Optional
import redis

# Cargar variables de entorno
load_dotenv()

# Variables de configuración de Redis
REDIS_HOST: Optional[str] = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

# Instancia global del cliente Redis (singleton pattern)
_redis_client: Optional[redis.Redis] = None
_redis_health_checked: bool = False


def validate_redis_config() -> None:
    """
    Valida que la configuración de Redis esté disponible.
    No valida la conexión, solo que las variables estén definidas.
    
    Raises:
        ValueError: Si alguna variable de entorno crítica no está configurada.
    """
    if not REDIS_HOST:
        raise ValueError("REDIS_HOST no está configurada en las variables de entorno")
    if not isinstance(REDIS_PORT, int) or REDIS_PORT <= 0:
        raise ValueError("REDIS_PORT debe ser un número entero positivo")


def get_redis_client() -> redis.Redis:
    """
    Obtiene o crea la instancia del cliente Redis.
    Implementa el patrón singleton para reutilizar la conexión.
    
    Returns:
        Instancia del cliente Redis
        
    Raises:
        ValueError: Si la configuración no está completa.
        redis.ConnectionError: Si no se puede conectar a Redis.
    """
    global _redis_client
    
    if _redis_client is None:
        validate_redis_config()
        
        # Crear cliente Redis
        _redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True,  # Decodificar respuestas como strings
            socket_connect_timeout=5,  # Timeout de conexión de 5 segundos
            socket_timeout=5,  # Timeout de operaciones de 5 segundos
        )
        
        # Verificar conexión
        try:
            _redis_client.ping()
        except redis.ConnectionError as e:
            _redis_client = None
            raise redis.ConnectionError(f"No se pudo conectar a Redis en {REDIS_HOST}:{REDIS_PORT}: {e}")
    
    return _redis_client


def close_redis_client() -> None:
    """
    Cierra la conexión del cliente Redis.
    Útil para cleanup en shutdown de la aplicación.
    """
    global _redis_client
    if _redis_client is not None:
        try:
            _redis_client.close()
        except:
            pass
        _redis_client = None


def ensure_redis_healthcheck() -> None:
    """
    Verifica que Redis esté disponible y funcionando.
    Lanza excepción si Redis no está disponible.
    
    Raises:
        redis.ConnectionError: Si Redis no está disponible.
    """
    global _redis_health_checked
    if not _redis_health_checked:
        client = get_redis_client()
        try:
            client.ping()
            _redis_health_checked = True
        except redis.ConnectionError as e:
            raise redis.ConnectionError(f"Redis no está disponible: {e}")

