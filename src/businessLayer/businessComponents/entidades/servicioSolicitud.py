from typing import List, Optional, Dict, Any
from src.businessLayer.businessEntities.solicitud import Solicitud
from src.dataLayer.dataAccesComponets.repositorioSolicitudes import (
    crear_solicitud as repo_crear_solicitud,
    obtener_solicitud_por_id as repo_obtener_por_id,
    listar_solicitudes as repo_listar_solicitudes,
    obtener_solicitudes_por_solicitante as repo_obtener_por_solicitante,
    actualizar_solicitud as repo_actualizar_solicitud,
    eliminar_solicitud as repo_eliminar_solicitud,
)


class ServicioSolicitud:
    """
    Servicio de aplicación para gestionar Solicitudes.
    Orquesta validaciones y delega persistencia al repositorio.
    """

    @staticmethod
    def crear(solicitud: Solicitud) -> Optional[Solicitud]:
        """
        Crea una nueva solicitud.
        Si la ubicación no tiene ID, la crea primero en la base de datos.
        Retorna la Solicitud con id asignado o None si hay error.
        """
        if not isinstance(solicitud, Solicitud):
            raise ValueError("El parámetro debe ser una instancia de Solicitud")
        if not solicitud.solicitante:
            raise ValueError("La solicitud debe tener un solicitante")
        if not solicitud.ubicacion:
            raise ValueError("La solicitud debe tener una ubicación")
        if not solicitud.solicitante.id:
            raise ValueError("El solicitante debe tener un ID (debe existir en la base de datos)")
        if not solicitud.fechaHora:
            raise ValueError("La solicitud debe tener una fecha y hora")
        
        # Si la ubicación no tiene ID, crearla primero
        if not solicitud.ubicacion.id:
            from src.dataLayer.dataAccesComponets.repositorioUbicacion import crear_ubicacion as repo_crear_ubicacion
            ubicacion_creada = repo_crear_ubicacion(solicitud.ubicacion)
            if ubicacion_creada is None:
                raise ValueError("Error al crear la ubicación")
            # Actualizar la solicitud con la ubicación que tiene ID
            solicitud.ubicacion = ubicacion_creada
        
        return repo_crear_solicitud(solicitud)

    @staticmethod
    def obtener_por_id(id_solicitud: int) -> Optional[Solicitud]:
        """
        Obtiene una solicitud por su ID.
        """
        if not isinstance(id_solicitud, int) or id_solicitud <= 0:
            raise ValueError("id_solicitud inválido")
        return repo_obtener_por_id(id_solicitud)

    @staticmethod
    def listar(limit: int = 50, offset: int = 0) -> List[Solicitud]:
        """
        Lista solicitudes con paginación.
        """
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_listar_solicitudes(limit=limit, offset=offset)

    @staticmethod
    def obtener_por_solicitante(id_solicitante: int, limit: int = 50, offset: int = 0) -> List[Solicitud]:
        """
        Obtiene todas las solicitudes de un solicitante específico.
        """
        if not isinstance(id_solicitante, int) or id_solicitante <= 0:
            raise ValueError("id_solicitante inválido")
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_obtener_por_solicitante(id_solicitante, limit=limit, offset=offset)

    @staticmethod
    def actualizar(id_solicitud: int, cambios: Dict[str, Any]) -> Optional[Solicitud]:
        """
        Actualiza campos de la solicitud.
        """
        if not isinstance(id_solicitud, int) or id_solicitud <= 0:
            raise ValueError("id_solicitud inválido")
        if not isinstance(cambios, dict) or not cambios:
            raise ValueError("Debe proporcionar un diccionario de cambios")
        
        return repo_actualizar_solicitud(id_solicitud, cambios)

    @staticmethod
    def eliminar(id_solicitud: int) -> bool:
        """
        Elimina una solicitud por su ID.
        """
        if not isinstance(id_solicitud, int) or id_solicitud < 0:
            raise ValueError("id_solicitud inválido")
        return repo_eliminar_solicitud(id_solicitud)

