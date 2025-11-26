from typing import List, Optional, Dict, Any
from src.businessLayer.businessEntities.ambulancia import Ambulancia
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
from src.dataLayer.dataAccesComponets.repositorioAmbulancia import (
    crear_ambulancia as repo_crear_ambulancia,
    obtener_ambulancia_por_id as repo_obtener_por_id,
    obtener_ambulancia_por_placa as repo_obtener_por_placa,
    obtener_ambulancia_por_operador as repo_obtener_por_operador,
    listar_ambulancias as repo_listar_ambulancias,
    listar_ambulancias_disponibles as repo_listar_disponibles,
    listar_ambulancias_por_tipo as repo_listar_por_tipo,
    actualizar_ambulancia as repo_actualizar_ambulancia,
    eliminar_ambulancia as repo_eliminar_ambulancia,
)


class ServicioAmbulancia:
    """
    Servicio de aplicación para gestionar Ambulancias.
    Orquesta validaciones y delega persistencia al repositorio.
    """

    @staticmethod
    def crear(ambulancia: Ambulancia) -> Optional[Ambulancia]:
        """
        Crea una nueva ambulancia.
        Si la ubicación existe y no tiene ID, la crea primero en la base de datos.
        Retorna la Ambulancia con id asignado o None si hay error.
        """
        if not isinstance(ambulancia, Ambulancia):
            raise ValueError("El parámetro debe ser una instancia de Ambulancia")
        if not ambulancia.placa or not ambulancia.placa.strip():
            raise ValueError("La ambulancia debe tener una placa")
        if not ambulancia.tipoAmbulancia:
            raise ValueError("La ambulancia debe tener un tipo")
        
        # Si la ubicación existe y no tiene ID, crearla primero
        if ambulancia.ubicacion and not ambulancia.ubicacion.id:
            from src.dataLayer.dataAccesComponets.repositorioUbicacion import crear_ubicacion as repo_crear_ubicacion
            ubicacion_creada = repo_crear_ubicacion(ambulancia.ubicacion)
            if ubicacion_creada is None:
                raise ValueError("Error al crear la ubicación")
            # Actualizar la ambulancia con la ubicación que tiene ID
            ambulancia.ubicacion = ubicacion_creada
        
        return repo_crear_ambulancia(ambulancia)

    @staticmethod
    def obtener_por_id(id_ambulancia: int) -> Optional[Ambulancia]:
        """
        Obtiene una ambulancia por su ID.
        """
        if not isinstance(id_ambulancia, int) or id_ambulancia <= 0:
            raise ValueError("id_ambulancia inválido")
        return repo_obtener_por_id(id_ambulancia)

    @staticmethod
    def obtener_por_placa(placa: str) -> Optional[Ambulancia]:
        """
        Obtiene una ambulancia por su placa.
        """
        if not placa or not isinstance(placa, str) or not placa.strip():
            raise ValueError("placa inválida")
        return repo_obtener_por_placa(placa.strip())

    @staticmethod
    def obtener_por_operador(id_operador_ambulancia: int) -> Optional[Ambulancia]:
        """
        Obtiene la ambulancia asignada a un operador de ambulancia.
        """
        if not isinstance(id_operador_ambulancia, int) or id_operador_ambulancia <= 0:
            raise ValueError("id_operador_ambulancia inválido")
        return repo_obtener_por_operador(id_operador_ambulancia)

    @staticmethod
    def listar(limit: int = 50, offset: int = 0) -> List[Ambulancia]:
        """
        Lista ambulancias con paginación.
        """
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_listar_ambulancias(limit=limit, offset=offset)

    @staticmethod
    def listar_disponibles(limit: int = 50, offset: int = 0) -> List[Ambulancia]:
        """
        Lista ambulancias disponibles con paginación.
        """
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_listar_disponibles(limit=limit, offset=offset)

    @staticmethod
    def listar_por_tipo(tipo: TipoAmbulancia, limit: int = 50, offset: int = 0) -> List[Ambulancia]:
        """
        Lista ambulancias por tipo con paginación.
        """
        if isinstance(tipo, str):
            tipo = TipoAmbulancia(tipo)
        if not isinstance(tipo, TipoAmbulancia):
            raise ValueError("tipo inválido")
        if limit <= 0:
            limit = 50
        if offset < 0:
            offset = 0
        return repo_listar_por_tipo(tipo, limit=limit, offset=offset)

    @staticmethod
    def actualizar(id_ambulancia: int, cambios: Dict[str, Any]) -> Optional[Ambulancia]:
        """
        Actualiza campos de la ambulancia.
        """
        if not isinstance(id_ambulancia, int) or id_ambulancia <= 0:
            raise ValueError("id_ambulancia inválido")
        if not isinstance(cambios, dict) or not cambios:
            raise ValueError("Debe proporcionar un diccionario de cambios")
        
        # Validar y convertir enum si es necesario
        if "tipoAmbulancia" in cambios:
            if isinstance(cambios["tipoAmbulancia"], str):
                cambios["tipoAmbulancia"] = TipoAmbulancia(cambios["tipoAmbulancia"])
            if not isinstance(cambios["tipoAmbulancia"], TipoAmbulancia):
                raise ValueError("tipoAmbulancia inválido")
        
        # Normalizar placa si está presente
        if "placa" in cambios and isinstance(cambios["placa"], str):
            cambios["placa"] = cambios["placa"].strip()
            if not cambios["placa"]:
                raise ValueError("La placa no puede estar vacía")
        
        return repo_actualizar_ambulancia(id_ambulancia, cambios)

    @staticmethod
    def eliminar(id_ambulancia: int) -> bool:
        """
        Elimina una ambulancia por su ID.
        """
        if not isinstance(id_ambulancia, int) or id_ambulancia < 0:
            raise ValueError("id_ambulancia inválido")
        return repo_eliminar_ambulancia(id_ambulancia)

