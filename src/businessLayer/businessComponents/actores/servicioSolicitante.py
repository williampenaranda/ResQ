from typing import List, Optional, Dict, Any
from src.businessLayer.businessEntities.solicitante import Solicitante
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento
from src.dataLayer.dataAccesComponets.repositorioSolicitantes import (
    crear_solicitante as repo_crear_solicitante,
    obtener_solicitante_por_id as repo_obtener_por_id,
    obtener_solicitante_por_documento as repo_obtener_por_documento,
    listar_solicitantes as repo_listar_solicitantes,
    actualizar_solicitante as repo_actualizar_solicitante,
    eliminar_solicitante as repo_eliminar_solicitante,
)


class ServicioSolicitante:
    """
    Servicio de aplicación para gestionar Solicitantes.
    Orquesta validaciones y delega persistencia al repositorio.
    """

    @staticmethod
    def crear(solicitante: Solicitante) -> Optional[Solicitante]:
        """
        Crea un nuevo solicitante.
        Retorna el Solicitante con id asignado o None si existe duplicado.
        """
        if not isinstance(solicitante, Solicitante):
            raise ValueError("El parámetro debe ser una instancia de Solicitante")
        if not solicitante.nombre or not solicitante.apellido:
            raise ValueError("El solicitante debe tener nombre y apellido")
        if not solicitante.numeroDocumento or not solicitante.tipoDocumento:
            raise ValueError("El solicitante debe tener tipo y número de documento")
        return repo_crear_solicitante(solicitante)

    @staticmethod
    def obtener_por_id(id_solicitante: int) -> Optional[Solicitante]:
        if not isinstance(id_solicitante, int) or id_solicitante <= 0:
            raise ValueError("id_solicitante inválido")
        return repo_obtener_por_id(id_solicitante)

    @staticmethod
    def obtener_por_documento(tipo: TipoDocumento, numero: str) -> Optional[Solicitante]:
        if isinstance(tipo, str):
            tipo = TipoDocumento(tipo)
        if not isinstance(tipo, TipoDocumento):
            raise ValueError("tipoDocumento inválido")
        if not numero or not isinstance(numero, str) or not numero.strip():
            raise ValueError("numeroDocumento inválido")
        return repo_obtener_por_documento(tipo, numero.strip())

    @staticmethod
    def listar(limit: int = 50, offset: int = 0) -> List[Solicitante]:
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_listar_solicitantes(limit=limit, offset=offset)

    @staticmethod
    def actualizar(id_solicitante: int, cambios: Dict[str, Any]) -> Optional[Solicitante]:
        if not isinstance(id_solicitante, int) or id_solicitante <= 0:
            raise ValueError("id_solicitante inválido")
        if not isinstance(cambios, dict) or not cambios:
            raise ValueError("Debe proporcionar un diccionario de cambios")
        # Normalizar strings
        if "numeroDocumento" in cambios and isinstance(cambios["numeroDocumento"], str):
            cambios["numeroDocumento"] = cambios["numeroDocumento"].strip()
        return repo_actualizar_solicitante(id_solicitante, cambios)

    @staticmethod
    def eliminar(id_solicitante: int) -> bool:
        if not isinstance(id_solicitante, int) or id_solicitante < 0:
            raise ValueError("id_solicitante inválido")
        return repo_eliminar_solicitante(id_solicitante)


