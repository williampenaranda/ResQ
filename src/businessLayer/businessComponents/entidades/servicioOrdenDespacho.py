"""
Servicio de aplicación para gestionar Órdenes de Despacho.
Orquesta validaciones y delega persistencia al repositorio.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from src.businessLayer.businessEntities.ordenDespacho import OrdenDespacho

from src.dataLayer.dataAccesComponets.repositorioOrdenDespacho import (
    crear_orden_despacho as repo_crear_orden_despacho,
    obtener_orden_despacho_por_id as repo_obtener_orden_despacho_por_id,
    listar_ordenes_despacho as repo_listar_ordenes_despacho,
    obtener_ordenes_por_emergencia as repo_obtener_ordenes_por_emergencia,
    obtener_ordenes_por_ambulancia as repo_obtener_ordenes_por_ambulancia,
    obtener_ordenes_por_operador_ambulancia as repo_obtener_ordenes_por_operador_ambulancia,
    obtener_ordenes_por_operador_emergencia as repo_obtener_ordenes_por_operador_emergencia,
    actualizar_orden_despacho as repo_actualizar_orden_despacho,
    eliminar_orden_despacho as repo_eliminar_orden_despacho,
)


class ServicioOrdenDespacho:
    """
    Servicio de aplicación para gestionar Órdenes de Despacho.
    Orquesta validaciones y delega persistencia al repositorio.
    """

    @staticmethod
    def crear(orden_despacho: OrdenDespacho) -> Optional[OrdenDespacho]:
        """
        Crea una nueva orden de despacho.
        """
        if not isinstance(orden_despacho, OrdenDespacho):
            raise ValueError("El parámetro debe ser una instancia de OrdenDespacho")
        
        if not orden_despacho.emergencia or not orden_despacho.emergencia.id:
            raise ValueError("La orden de despacho debe tener una emergencia con ID válido")
        
        if not orden_despacho.ambulancia or not orden_despacho.ambulancia.id:
            raise ValueError("La orden de despacho debe tener una ambulancia con ID válido")
        
        if not orden_despacho.operadorAmbulancia or not orden_despacho.operadorAmbulancia.id:
            raise ValueError("La orden de despacho debe tener un operador de ambulancia con ID válido")
        
        if not orden_despacho.operadorEmergencia or not orden_despacho.operadorEmergencia.id:
            raise ValueError("La orden de despacho debe tener un operador de emergencia con ID válido")
        
        if not orden_despacho.fechaHora or not isinstance(orden_despacho.fechaHora, datetime):
            raise ValueError("La orden de despacho debe tener una fecha y hora válida")
        
        return repo_crear_orden_despacho(orden_despacho)

    @staticmethod
    def obtener_por_id(id_orden: int) -> Optional[OrdenDespacho]:
        """
        Obtiene una orden de despacho por su ID.
        """
        if not isinstance(id_orden, int) or id_orden <= 0:
            raise ValueError("id_orden inválido")
        return repo_obtener_orden_despacho_por_id(id_orden)

    @staticmethod
    def listar(limit: int = 50, offset: int = 0) -> List[OrdenDespacho]:
        """
        Lista órdenes de despacho con paginación.
        """
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_listar_ordenes_despacho(limit=limit, offset=offset)

    @staticmethod
    def obtener_por_emergencia(id_emergencia: int, limit: int = 50, offset: int = 0) -> List[OrdenDespacho]:
        """
        Obtiene órdenes de despacho filtradas por emergencia.
        """
        if not isinstance(id_emergencia, int) or id_emergencia <= 0:
            raise ValueError("id_emergencia inválido")
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_obtener_ordenes_por_emergencia(id_emergencia, limit=limit, offset=offset)

    @staticmethod
    def obtener_por_ambulancia(id_ambulancia: int, limit: int = 50, offset: int = 0) -> List[OrdenDespacho]:
        """
        Obtiene órdenes de despacho filtradas por ambulancia.
        """
        if not isinstance(id_ambulancia, int) or id_ambulancia <= 0:
            raise ValueError("id_ambulancia inválido")
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_obtener_ordenes_por_ambulancia(id_ambulancia, limit=limit, offset=offset)

    @staticmethod
    def obtener_por_operador_ambulancia(id_operador: int, limit: int = 50, offset: int = 0) -> List[OrdenDespacho]:
        """
        Obtiene órdenes de despacho asignadas a un operador de ambulancia específico.
        """
        if not isinstance(id_operador, int) or id_operador <= 0:
            raise ValueError("id_operador inválido")
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_obtener_ordenes_por_operador_ambulancia(id_operador, limit=limit, offset=offset)

    @staticmethod
    def obtener_por_operador_emergencia(id_operador: int, limit: int = 50, offset: int = 0) -> List[OrdenDespacho]:
        """
        Obtiene órdenes de despacho creadas por un operador de emergencia específico.
        """
        if not isinstance(id_operador, int) or id_operador <= 0:
            raise ValueError("id_operador inválido")
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_obtener_ordenes_por_operador_emergencia(id_operador, limit=limit, offset=offset)

    @staticmethod
    def actualizar(id_orden: int, cambios: Dict[str, Any]) -> Optional[OrdenDespacho]:
        """
        Actualiza una orden de despacho con los cambios proporcionados.
        """
        if not isinstance(id_orden, int) or id_orden <= 0:
            raise ValueError("id_orden inválido")
        if not isinstance(cambios, dict) or not cambios:
            raise ValueError("Debe proporcionar un diccionario de cambios")
        
        # Validar fechaHora si está en los cambios
        if "fechaHora" in cambios:
            if not isinstance(cambios["fechaHora"], datetime):
                raise ValueError("fechaHora debe ser una instancia de datetime")
        
        # Validar IDs si están en los cambios
        if "emergencia_id" in cambios:
            if not isinstance(cambios["emergencia_id"], int) or cambios["emergencia_id"] <= 0:
                raise ValueError("emergencia_id inválido")
        
        if "ambulancia_id" in cambios:
            if not isinstance(cambios["ambulancia_id"], int) or cambios["ambulancia_id"] <= 0:
                raise ValueError("ambulancia_id inválido")
        
        if "operador_ambulancia_id" in cambios:
            if not isinstance(cambios["operador_ambulancia_id"], int) or cambios["operador_ambulancia_id"] <= 0:
                raise ValueError("operador_ambulancia_id inválido")
        
        if "operador_emergencia_id" in cambios:
            if not isinstance(cambios["operador_emergencia_id"], int) or cambios["operador_emergencia_id"] <= 0:
                raise ValueError("operador_emergencia_id inválido")
        
        return repo_actualizar_orden_despacho(id_orden, cambios)

    @staticmethod
    def eliminar(id_orden: int) -> bool:
        """
        Elimina una orden de despacho por su ID.
        """
        if not isinstance(id_orden, int) or id_orden <= 0:
            raise ValueError("id_orden inválido")
        return repo_eliminar_orden_despacho(id_orden)
