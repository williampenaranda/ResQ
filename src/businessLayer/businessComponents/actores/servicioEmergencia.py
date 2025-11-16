"""
Servicio de aplicación para gestionar Emergencias.
Orquesta validaciones y delega persistencia al repositorio.
"""

from typing import List, Optional, Dict, Any

from src.businessLayer.businessEntities.emergencia import Emergencia
from src.businessLayer.businessEntities.enums.estadoEmergencia import EstadoEmergencia
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
from src.businessLayer.businessEntities.enums.nivelPrioridad import NivelPrioridad

from src.dataLayer.dataAccesComponets.repositorioEmergencias import (
    crear_emergencia as repo_crear_emergencia,
    obtener_emergencia_por_id as repo_obtener_emergencia_por_id,
    listar_emergencias as repo_listar_emergencias,
    obtener_emergencias_por_estado as repo_obtener_emergencias_por_estado,
    obtener_emergencias_por_operador as repo_obtener_emergencias_por_operador,
    obtener_emergencias_por_solicitud as repo_obtener_emergencias_por_solicitud,
    actualizar_emergencia as repo_actualizar_emergencia,
    eliminar_emergencia as repo_eliminar_emergencia,
)


class ServicioEmergencia:
    """
    Servicio de aplicación para gestionar Emergencias.
    Orquesta validaciones y delega persistencia al repositorio.
    """

    @staticmethod
    def crear(emergencia: Emergencia) -> Optional[Emergencia]:
        """
        Crea una nueva emergencia.
        """
        if not isinstance(emergencia, Emergencia):
            raise ValueError("El parámetro debe ser una instancia de Emergencia")
        
        if not emergencia.solicitud or not emergencia.solicitud.id:
            raise ValueError("La emergencia debe tener una solicitud con ID válido")
        
        if not emergencia.paciente or not emergencia.paciente.id:
            raise ValueError("La emergencia debe tener un paciente con ID válido")
        
        if not emergencia.id_operador or emergencia.id_operador <= 0:
            raise ValueError("La emergencia debe tener un operador con ID válido")
        
        if not emergencia.descripcion or not emergencia.descripcion.strip():
            raise ValueError("La emergencia debe tener una descripción")
        
        if not isinstance(emergencia.estado, EstadoEmergencia):
            raise ValueError("El estado debe ser una instancia de EstadoEmergencia")
        
        if not isinstance(emergencia.tipoAmbulancia, TipoAmbulancia):
            raise ValueError("El tipo de ambulancia debe ser una instancia de TipoAmbulancia")
        
        if not isinstance(emergencia.nivelPrioridad, NivelPrioridad):
            raise ValueError("El nivel de prioridad debe ser una instancia de NivelPrioridad")
        
        return repo_crear_emergencia(emergencia)

    @staticmethod
    def obtener_por_id(id_emergencia: int) -> Optional[Emergencia]:
        """
        Obtiene una emergencia por su ID.
        """
        if not isinstance(id_emergencia, int) or id_emergencia <= 0:
            raise ValueError("id_emergencia inválido")
        return repo_obtener_emergencia_por_id(id_emergencia)

    @staticmethod
    def listar(limit: int = 50, offset: int = 0) -> List[Emergencia]:
        """
        Lista emergencias con paginación.
        """
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_listar_emergencias(limit=limit, offset=offset)

    @staticmethod
    def obtener_por_estado(estado: EstadoEmergencia, limit: int = 50, offset: int = 0) -> List[Emergencia]:
        """
        Obtiene emergencias filtradas por estado.
        """
        if isinstance(estado, str):
            estado = EstadoEmergencia(estado)
        if not isinstance(estado, EstadoEmergencia):
            raise ValueError("estado inválido")
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_obtener_emergencias_por_estado(estado, limit=limit, offset=offset)

    @staticmethod
    def obtener_por_operador(id_operador: int, limit: int = 50, offset: int = 0) -> List[Emergencia]:
        """
        Obtiene emergencias asignadas a un operador específico.
        """
        if not isinstance(id_operador, int) or id_operador <= 0:
            raise ValueError("id_operador inválido")
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_obtener_emergencias_por_operador(id_operador, limit=limit, offset=offset)

    @staticmethod
    def obtener_por_solicitud(id_solicitud: int) -> Optional[Emergencia]:
        """
        Obtiene la emergencia asociada a una solicitud específica.
        """
        if not isinstance(id_solicitud, int) or id_solicitud <= 0:
            raise ValueError("id_solicitud inválido")
        return repo_obtener_emergencias_por_solicitud(id_solicitud)

    @staticmethod
    def actualizar(id_emergencia: int, cambios: Dict[str, Any]) -> Optional[Emergencia]:
        """
        Actualiza una emergencia con los cambios proporcionados.
        """
        if not isinstance(id_emergencia, int) or id_emergencia <= 0:
            raise ValueError("id_emergencia inválido")
        if not isinstance(cambios, dict) or not cambios:
            raise ValueError("Debe proporcionar un diccionario de cambios")
        
        # Validar y convertir enums si es necesario
        if "estado" in cambios:
            if isinstance(cambios["estado"], str):
                cambios["estado"] = EstadoEmergencia(cambios["estado"])
            if not isinstance(cambios["estado"], EstadoEmergencia):
                raise ValueError("estado inválido")
        
        if "tipoAmbulancia" in cambios:
            if isinstance(cambios["tipoAmbulancia"], str):
                cambios["tipoAmbulancia"] = TipoAmbulancia(cambios["tipoAmbulancia"])
            if not isinstance(cambios["tipoAmbulancia"], TipoAmbulancia):
                raise ValueError("tipoAmbulancia inválido")
        
        if "nivelPrioridad" in cambios:
            if isinstance(cambios["nivelPrioridad"], str):
                cambios["nivelPrioridad"] = NivelPrioridad(cambios["nivelPrioridad"])
            if not isinstance(cambios["nivelPrioridad"], NivelPrioridad):
                raise ValueError("nivelPrioridad inválido")
        
        if "descripcion" in cambios and isinstance(cambios["descripcion"], str):
            cambios["descripcion"] = cambios["descripcion"].strip()
            if not cambios["descripcion"]:
                raise ValueError("La descripción no puede estar vacía")
        
        if "id_operador" in cambios:
            if not isinstance(cambios["id_operador"], int) or cambios["id_operador"] <= 0:
                raise ValueError("id_operador inválido")
        
        return repo_actualizar_emergencia(id_emergencia, cambios)

    @staticmethod
    def eliminar(id_emergencia: int) -> bool:
        """
        Elimina una emergencia por su ID.
        """
        if not isinstance(id_emergencia, int) or id_emergencia <= 0:
            raise ValueError("id_emergencia inválido")
        return repo_eliminar_emergencia(id_emergencia)

