from typing import List, Optional, Dict, Any
from src.businessLayer.businessEntities.ubicacion import Ubicacion
from src.dataLayer.dataAccesComponets.repositorioUbicacion import (
    crear_ubicacion as repo_crear_ubicacion,
    obtener_ubicacion_por_id as repo_obtener_por_id,
    listar_ubicaciones as repo_listar_ubicaciones,
    actualizar_ubicacion as repo_actualizar_ubicacion,
    eliminar_ubicacion as repo_eliminar_ubicacion,
)


class ServicioUbicacion:
    """
    Servicio de aplicación para gestionar Ubicaciones.
    Orquesta validaciones y delega persistencia al repositorio.
    """

    @staticmethod
    def crear(ubicacion: Ubicacion) -> Optional[Ubicacion]:
        """
        Crea una nueva ubicación.
        Retorna la Ubicacion con id asignado o None si hay error.
        """
        if not isinstance(ubicacion, Ubicacion):
            raise ValueError("El parámetro debe ser una instancia de Ubicacion")
        if ubicacion.latitud is None or ubicacion.longitud is None:
            raise ValueError("La ubicación debe tener latitud y longitud")
        if ubicacion.latitud < -90 or ubicacion.latitud > 90:
            raise ValueError("La latitud debe estar entre -90 y 90 grados")
        if ubicacion.longitud < -180 or ubicacion.longitud > 180:
            raise ValueError("La longitud debe estar entre -180 y 180 grados")
        return repo_crear_ubicacion(ubicacion)

    @staticmethod
    def obtener_por_id(id_ubicacion: int) -> Optional[Ubicacion]:
        """
        Obtiene una ubicación por su ID.
        """
        if not isinstance(id_ubicacion, int) or id_ubicacion <= 0:
            raise ValueError("id_ubicacion inválido")
        return repo_obtener_por_id(id_ubicacion)

    @staticmethod
    def listar(limit: int = 50, offset: int = 0) -> List[Ubicacion]:
        """
        Lista ubicaciones con paginación.
        """
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_listar_ubicaciones(limit=limit, offset=offset)

    @staticmethod
    def actualizar(id_ubicacion: int, cambios: Dict[str, Any]) -> Optional[Ubicacion]:
        """
        Actualiza campos de la ubicación.
        """
        if not isinstance(id_ubicacion, int) or id_ubicacion <= 0:
            raise ValueError("id_ubicacion inválido")
        if not isinstance(cambios, dict) or not cambios:
            raise ValueError("Debe proporcionar un diccionario de cambios")
        
        # Validar latitud si está presente
        if "latitud" in cambios:
            latitud = cambios["latitud"]
            if not isinstance(latitud, (int, float)) or latitud < -90 or latitud > 90:
                raise ValueError("La latitud debe estar entre -90 y 90 grados")
        
        # Validar longitud si está presente
        if "longitud" in cambios:
            longitud = cambios["longitud"]
            if not isinstance(longitud, (int, float)) or longitud < -180 or longitud > 180:
                raise ValueError("La longitud debe estar entre -180 y 180 grados")
        
        return repo_actualizar_ubicacion(id_ubicacion, cambios)

    @staticmethod
    def eliminar(id_ubicacion: int) -> bool:
        """
        Elimina una ubicación por su ID.
        """
        if not isinstance(id_ubicacion, int) or id_ubicacion < 0:
            raise ValueError("id_ubicacion inválido")
        return repo_eliminar_ubicacion(id_ubicacion)

