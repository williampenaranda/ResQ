"""
Workflow para procesar la ubicación de una ambulancia.
Almacena la ubicación en Redis para acceso rápido en tiempo real.
"""

from datetime import datetime, timezone
from src.businessLayer.businessComponents.entidades.servicioAmbulancia import ServicioAmbulancia
from src.businessLayer.businessComponents.cache.servicioUbicacionCache import ServicioUbicacionCache
import redis


class ProcesarUbicacionAmbulancia:
    """
    Workflow para procesar y actualizar la ubicación de una ambulancia en Redis.
    """

    @staticmethod
    def procesar_ubicacion(id_ambulancia: int, latitud: float, longitud: float) -> None:
        """
        Procesa una nueva ubicación de una ambulancia y la guarda en Redis.
        Solo valida que la ambulancia exista, no actualiza la base de datos.

        Args:
            id_ambulancia: ID de la ambulancia
            latitud: Latitud de la ubicación (-90 a 90)
            longitud: Longitud de la ubicación (-180 a 180)

        Raises:
            ValueError: Si la ambulancia no existe, las coordenadas son inválidas
            redis.RedisError: Si hay error al guardar en Redis
        """
        # Validar coordenadas
        if not isinstance(latitud, (int, float)) or latitud < -90 or latitud > 90:
            raise ValueError("La latitud debe estar entre -90 y 90 grados")
        if not isinstance(longitud, (int, float)) or longitud < -180 or longitud > 180:
            raise ValueError("La longitud debe estar entre -180 y 180 grados")

        # Validar que la ambulancia exista (solo verificación, no actualización)
        ambulancia = ServicioAmbulancia.obtener_por_id(id_ambulancia)
        if not ambulancia:
            raise ValueError(f"Ambulancia con id {id_ambulancia} no encontrada")

        # Guardar ubicación en Redis (última ubicación en memoria)
        try:
            ServicioUbicacionCache.guardar_ubicacion(
                id_ambulancia=id_ambulancia,
                latitud=latitud,
                longitud=longitud,
                timestamp=datetime.now(timezone.utc)
            )
        except redis.RedisError as e:
            raise redis.RedisError(f"Error al guardar ubicación en Redis: {e}")

