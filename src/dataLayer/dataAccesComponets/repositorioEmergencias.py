"""
Repositorio de acceso a datos para Emergencias.

Proporciona operaciones CRUD usando SQLAlchemy y mapea hacia/desde
la entidad Pydantic `Emergencia` de la capa de negocio.
"""

from typing import List, Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.dataLayer.bd import SessionLocal
from src.dataLayer.models.modeloEmergencia import Emergencia as EmergenciaDB
from src.businessLayer.businessEntities.emergencia import Emergencia as EmergenciaBE
from src.businessLayer.businessEntities.enums.estadoEmergencia import EstadoEmergencia
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
from src.businessLayer.businessEntities.enums.nivelPrioridad import NivelPrioridad
from src.dataLayer.dataAccesComponets.repositorioSolicitudes import obtener_solicitud_por_id
from src.dataLayer.dataAccesComponets.repositorioSolicitantes import obtener_solicitante_por_id
from src.dataLayer.dataAccesComponets.repositorioOperadorEmergencia import obtener_operador_por_id


# ========================= Helpers de mapeo =========================

def _mapear_be_a_db(emergencia: EmergenciaBE) -> EmergenciaDB:
    """
    Mapea una Emergencia de la capa de negocio a la capa de datos.
    Requiere que la solicitud, operador y solicitante ya existan en la BD (tengan ID).
    """
    if not emergencia.solicitud.id:
        raise ValueError("La solicitud debe tener un ID para crear la emergencia")
    if not emergencia.solicitante.id:
        raise ValueError("El solicitante debe tener un ID para crear la emergencia")
    if not emergencia.id_operador or emergencia.id_operador <= 0:
        raise ValueError("El operador debe tener un ID válido")
    
    return EmergenciaDB(
        solicitud_id=emergencia.solicitud.id,
        id_operador=emergencia.id_operador,
        solicitante_id=emergencia.solicitante.id,
        estado=emergencia.estado,
        tipoAmbulancia=emergencia.tipoAmbulancia,
        nivelPrioridad=emergencia.nivelPrioridad,
        descripcion=emergencia.descripcion
    )


def _mapear_db_a_be(db_obj: EmergenciaDB) -> EmergenciaBE:
    """
    Mapea una Emergencia de la capa de datos a la capa de negocio.
    Carga los objetos completos de Solicitud, OperadorEmergencia y Solicitante desde sus repositorios.
    """
    # Cargar la solicitud completa
    solicitud = obtener_solicitud_por_id(db_obj.solicitud_id)
    if not solicitud:
        raise RuntimeError(f"Solicitud con id {db_obj.solicitud_id} no encontrada")
    
    # Cargar el operador completo
    operador = obtener_operador_por_id(db_obj.id_operador)
    if not operador:
        raise RuntimeError(f"Operador con id {db_obj.id_operador} no encontrado")
    
    # Cargar el solicitante completo
    solicitante = obtener_solicitante_por_id(db_obj.solicitante_id)
    if not solicitante:
        raise RuntimeError(f"Solicitante con id {db_obj.solicitante_id} no encontrado")
    
    return EmergenciaBE(
        id=db_obj.id,
        solicitud=solicitud,
        estado=EstadoEmergencia(db_obj.estado) if isinstance(db_obj.estado, str) else db_obj.estado,
        tipoAmbulancia=TipoAmbulancia(db_obj.tipoAmbulancia) if isinstance(db_obj.tipoAmbulancia, str) else db_obj.tipoAmbulancia,
        nivelPrioridad=NivelPrioridad(db_obj.nivelPrioridad) if isinstance(db_obj.nivelPrioridad, str) else db_obj.nivelPrioridad,
        descripcion=db_obj.descripcion,
        id_operador=db_obj.id_operador,
        solicitante=solicitante
    )


# ========================= Operaciones CRUD =========================

def crear_emergencia(emergencia: EmergenciaBE) -> Optional[EmergenciaBE]:
    """
    Crea una emergencia. Devuelve el modelo Pydantic con el id asignado.
    Retorna None en caso de error de integridad (FK inválida).
    """
    if not isinstance(emergencia, EmergenciaBE):
        raise ValueError("El parámetro debe ser una instancia de Emergencia")

    sesion: Session = SessionLocal()
    try:
        db_obj = _mapear_be_a_db(emergencia)
        sesion.add(db_obj)
        sesion.commit()
        sesion.refresh(db_obj)
        return _mapear_db_a_be(db_obj)
    except IntegrityError:
        sesion.rollback()
        return None
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al crear emergencia: {e}")
    finally:
        sesion.close()


def obtener_emergencia_por_id(id_emergencia: int) -> Optional[EmergenciaBE]:
    """
    Obtiene una emergencia por su ID.
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(EmergenciaDB, id_emergencia)
        return _mapear_db_a_be(db_obj) if db_obj else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener emergencia por id: {e}")
    finally:
        sesion.close()


def listar_emergencias(limit: int = 50, offset: int = 0) -> List[EmergenciaBE]:
    """
    Lista emergencias con paginación, ordenadas por fecha de creación más reciente.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(EmergenciaDB).order_by(EmergenciaDB.fechaCreacion.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al listar emergencias: {e}")
    finally:
        sesion.close()


def obtener_emergencias_por_estado(estado: EstadoEmergencia, limit: int = 50, offset: int = 0) -> List[EmergenciaBE]:
    """
    Obtiene todas las emergencias con un estado específico.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(EmergenciaDB).filter(
            EmergenciaDB.estado == estado
        ).order_by(EmergenciaDB.fechaCreacion.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener emergencias por estado: {e}")
    finally:
        sesion.close()


def obtener_emergencias_por_operador(id_operador: int, limit: int = 50, offset: int = 0) -> List[EmergenciaBE]:
    """
    Obtiene todas las emergencias asignadas a un operador específico.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(EmergenciaDB).filter(
            EmergenciaDB.id_operador == id_operador
        ).order_by(EmergenciaDB.fechaCreacion.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener emergencias por operador: {e}")
    finally:
        sesion.close()


def obtener_emergencias_por_solicitante(id_solicitante: int, limit: int = 50, offset: int = 0) -> List[EmergenciaBE]:
    """
    Obtiene todas las emergencias realizadas por un solicitante específico.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(EmergenciaDB).filter(
            EmergenciaDB.solicitante_id == id_solicitante
        ).order_by(EmergenciaDB.fechaCreacion.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener emergencias por solicitante: {e}")
    finally:
        sesion.close()


def obtener_emergencias_por_solicitud(id_solicitud: int) -> Optional[EmergenciaBE]:
    """
    Obtiene la emergencia asociada a una solicitud específica.
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.query(EmergenciaDB).filter(
            EmergenciaDB.solicitud_id == id_solicitud
        ).first()
        return _mapear_db_a_be(db_obj) if db_obj else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener emergencia por solicitud: {e}")
    finally:
        sesion.close()


def actualizar_emergencia(id_emergencia: int, cambios: dict) -> Optional[EmergenciaBE]:
    """
    Actualiza campos de la emergencia. `cambios` puede incluir:
    estado, tipoAmbulancia, nivelPrioridad, descripcion, id_operador, solicitud_id, solicitante_id.
    """
    if not cambios:
        raise ValueError("No hay cambios para aplicar")

    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(EmergenciaDB, id_emergencia)
        if not db_obj:
            return None

        # Validar que las FKs existan si se están actualizando
        if "solicitud_id" in cambios:
            solicitud = obtener_solicitud_por_id(cambios["solicitud_id"])
            if not solicitud:
                raise ValueError(f"Solicitud con id {cambios['solicitud_id']} no existe")
        
        if "id_operador" in cambios:
            operador = obtener_operador_por_id(cambios["id_operador"])
            if not operador:
                raise ValueError(f"Operador con id {cambios['id_operador']} no existe")
        
        if "solicitante_id" in cambios:
            solicitante = obtener_solicitante_por_id(cambios["solicitante_id"])
            if not solicitante:
                raise ValueError(f"Solicitante con id {cambios['solicitante_id']} no existe")

        # Convertir enums si es necesario
        if "estado" in cambios and isinstance(cambios["estado"], str):
            cambios["estado"] = EstadoEmergencia(cambios["estado"])
        if "tipoAmbulancia" in cambios and isinstance(cambios["tipoAmbulancia"], str):
            cambios["tipoAmbulancia"] = TipoAmbulancia(cambios["tipoAmbulancia"])
        if "nivelPrioridad" in cambios and isinstance(cambios["nivelPrioridad"], str):
            cambios["nivelPrioridad"] = NivelPrioridad(cambios["nivelPrioridad"])

        for campo, valor in cambios.items():
            if hasattr(db_obj, campo):
                setattr(db_obj, campo, valor)

        sesion.commit()
        sesion.refresh(db_obj)
        return _mapear_db_a_be(db_obj)
    except IntegrityError:
        sesion.rollback()
        return None
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al actualizar emergencia: {e}")
    finally:
        sesion.close()


def eliminar_emergencia(id_emergencia: int) -> bool:
    """
    Elimina una emergencia por su ID.
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(EmergenciaDB, id_emergencia)
        if not db_obj:
            return False
        sesion.delete(db_obj)
        sesion.commit()
        return True
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al eliminar emergencia: {e}")
    finally:
        sesion.close()

