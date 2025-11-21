"""
Servicio de cache para ubicaciones de ambulancias usando Redis.
Almacena solo la última ubicación de cada ambulancia en memoria.
"""

import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from src.businessLayer.businessComponents.cache.configRedis import get_redis_client


class ServicioUbicacionCache:
    """
    Servicio para gestionar el cache de ubicaciones de ambulancias en Redis.
    """

    @staticmethod
    def _get_key(id_ambulancia: int) -> str:
        """
        Genera la key de Redis para una ambulancia.
        
        Args:
            id_ambulancia: ID de la ambulancia
            
        Returns:
            Key de Redis en formato: ambulancia:{id_ambulancia}:ubicacion
        """
        return f"ambulancia:{id_ambulancia}:ubicacion"

    @staticmethod
    def guardar_ubicacion(
        id_ambulancia: int,
        latitud: float,
        longitud: float,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Guarda la última ubicación de una ambulancia en Redis.
        
        Args:
            id_ambulancia: ID de la ambulancia
            latitud: Latitud de la ubicación
            longitud: Longitud de la ubicación
            timestamp: Timestamp de la ubicación (si None, usa el actual)
            
        Raises:
            redis.RedisError: Si hay error al guardar en Redis
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        # Preparar datos como JSON
        datos = {
            "latitud": latitud,
            "longitud": longitud,
            "timestamp": timestamp.isoformat()
        }
        
        key = ServicioUbicacionCache._get_key(id_ambulancia)
        client = get_redis_client()
        
        # Guardar en Redis (sin TTL, ya que solo necesitamos la última ubicación)
        client.set(key, json.dumps(datos))

    @staticmethod
    def obtener_ubicacion(id_ambulancia: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene la última ubicación de una ambulancia desde Redis.
        
        Args:
            id_ambulancia: ID de la ambulancia
            
        Returns:
            Diccionario con latitud, longitud y timestamp, o None si no existe
            
        Raises:
            redis.RedisError: Si hay error al leer de Redis
        """
        key = ServicioUbicacionCache._get_key(id_ambulancia)
        client = get_redis_client()
        
        datos_json = client.get(key)
        if datos_json is None:
            return None
        
        try:
            return json.loads(datos_json)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def eliminar_ubicacion(id_ambulancia: int) -> None:
        """
        Elimina la ubicación de una ambulancia de Redis.
        Útil cuando la ambulancia se desconecta.
        
        Args:
            id_ambulancia: ID de la ambulancia
            
        Raises:
            redis.RedisError: Si hay error al eliminar de Redis
        """
        key = ServicioUbicacionCache._get_key(id_ambulancia)
        client = get_redis_client()
        client.delete(key)

