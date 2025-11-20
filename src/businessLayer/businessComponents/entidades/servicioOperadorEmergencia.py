from typing import List, Optional, Dict, Any

from src.businessLayer.businessEntities.operadorEmergencia import OperadorEmergencia
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento

from src.dataLayer.dataAccesComponets.repositorioOperadorEmergencia import (
    crear_operador as repo_crear_operador,
    obtener_operador_por_id as repo_obtener_operador_por_id,
    obtener_operador_por_documento as repo_obtener_operador_por_documento,
    listar_operadores as repo_listar_operadores,
    actualizar_operador as repo_actualizar_operador,
    eliminar_operador as repo_eliminar_operador,
)


class ServicioOperadorEmergencia:
    """
    Servicio de aplicación para gestionar Operadores de Emergencia.
    Orquesta validaciones y delega persistencia al repositorio.
    """

    @staticmethod
    def crear(operador: OperadorEmergencia) -> Optional[OperadorEmergencia]:
        if not isinstance(operador, OperadorEmergencia):
            raise ValueError("El parámetro debe ser una instancia de OperadorEmergencia")
        if not operador.nombre or not operador.apellido:
            raise ValueError("El operador debe tener nombre y apellido")
        if not operador.numeroDocumento or not operador.tipoDocumento:
            raise ValueError("El operador debe tener tipo y número de documento")
        if operador.disponibilidad is None:
            raise ValueError("El operador debe indicar disponibilidad")
        return repo_crear_operador(operador)

    @staticmethod
    def obtener_por_id(id_operador: int) -> Optional[OperadorEmergencia]:
        if not isinstance(id_operador, int) or id_operador <= 0:
            raise ValueError("id_operador inválido")
        return repo_obtener_operador_por_id(id_operador)

    @staticmethod
    def obtener_por_documento(tipo: TipoDocumento, numero: str) -> Optional[OperadorEmergencia]:
        if isinstance(tipo, str):
            tipo = TipoDocumento(tipo)
        if not isinstance(tipo, TipoDocumento):
            raise ValueError("tipoDocumento inválido")
        if not numero or not isinstance(numero, str) or not numero.strip():
            raise ValueError("numeroDocumento inválido")
        return repo_obtener_operador_por_documento(tipo, numero.strip())

    @staticmethod
    def listar(limit: int = 50, offset: int = 0) -> List[OperadorEmergencia]:
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_listar_operadores(limit=limit, offset=offset)

    @staticmethod
    def actualizar(id_operador: int, cambios: Dict[str, Any]) -> Optional[OperadorEmergencia]:
        if not isinstance(id_operador, int) or id_operador <= 0:
            raise ValueError("id_operador inválido")
        if not isinstance(cambios, dict) or not cambios:
            raise ValueError("Debe proporcionar un diccionario de cambios")
        if "numeroDocumento" in cambios and isinstance(cambios["numeroDocumento"], str):
            cambios["numeroDocumento"] = cambios["numeroDocumento"].strip()
        if "tipoDocumento" in cambios and isinstance(cambios["tipoDocumento"], str):
            cambios["tipoDocumento"] = TipoDocumento(cambios["tipoDocumento"])
        return repo_actualizar_operador(id_operador, cambios)

    @staticmethod
    def eliminar(id_operador: int) -> bool:
        if not isinstance(id_operador, int) or id_operador <= 0:
            raise ValueError("id_operador inválido")
        return repo_eliminar_operador(id_operador)

