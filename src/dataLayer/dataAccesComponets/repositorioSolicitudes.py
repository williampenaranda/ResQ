"""
Repositorio de acceso a datos para Solicitudes.

Proporciona operaciones CRUD usando SQLAlchemy y mapea hacia/desde
la entidad Pydantic `Solicitud` de la capa de negocio.
"""

from typing import List, Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.dataLayer.bd import SessionLocal
from src.dataLayer.models.modeloSolicitud import Solicitud as SolicitudDB
from src.businessLayer.businessEntities.solicitud import Solicitud as SolicitudBE
from src.dataLayer.dataAccesComponets.repositorioSolicitantes import obtener_solicitante_por_id
from src.dataLayer.dataAccesComponets.repositorioUbicacion import obtener_ubicacion_por_id


# ========================= Helpers de mapeo =========================

def _mapear_be_a_db(solicitud: SolicitudBE) -> SolicitudDB:
    """
    Mapea una Solicitud de la capa de negocio a la capa de datos.
    Requiere que el solicitante y ubicacion ya existan en la BD (tengan ID).
    Si la ubicación no tiene ID, se debe crear primero antes de llamar a esta función.
    """
    if not solicitud.solicitante.id:
        raise ValueError("El solicitante debe tener un ID para crear la solicitud")
    if not solicitud.ubicacion.id:
        raise ValueError("La ubicación debe tener un ID para crear la solicitud. Debe crearse primero en la base de datos.")
    
    return SolicitudDB(
        solicitante_id=solicitud.solicitante.id,
        ubicacion_id=solicitud.ubicacion.id,
        fechaHora=solicitud.get_fecha_hora()
    )


def _mapear_db_a_be(db_obj: SolicitudDB) -> SolicitudBE:
    """
    Mapea una Solicitud de la capa de datos a la capa de negocio.
    Carga los objetos completos de Solicitante y Ubicacion desde sus repositorios.
    """
    # Cargar el solicitante completo
    solicitante = obtener_solicitante_por_id(db_obj.solicitante_id)
    if not solicitante:
        raise RuntimeError(f"Solicitante con id {db_obj.solicitante_id} no encontrado")
    
    # Cargar la ubicación completa
    ubicacion = obtener_ubicacion_por_id(db_obj.ubicacion_id)
    if not ubicacion:
        raise RuntimeError(f"Ubicación con id {db_obj.ubicacion_id} no encontrada")
    
    return SolicitudBE(
        id=db_obj.id,
        solicitante=solicitante,
        fechaHora=db_obj.fechaHora,
        ubicacion=ubicacion
    )


# ========================= Operaciones CRUD =========================

def crear_solicitud(solicitud: SolicitudBE) -> Optional[SolicitudBE]:
    """
    Crea una solicitud. Devuelve el modelo Pydantic con el id asignado.
    Retorna None en caso de error de integridad (FK inválida).
    """
    if not isinstance(solicitud, SolicitudBE):
        raise ValueError("El parámetro debe ser una instancia de Solicitud")

    sesion: Session = SessionLocal()
    try:
        db_obj = _mapear_be_a_db(solicitud)
        sesion.add(db_obj)
        sesion.commit()
        sesion.refresh(db_obj)
        return _mapear_db_a_be(db_obj)
    except IntegrityError:
        sesion.rollback()
        return None
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al crear solicitud: {e}")
    finally:
        sesion.close()


def obtener_solicitud_por_id(id_solicitud: int) -> Optional[SolicitudBE]:
    """
    Obtiene una solicitud por su ID.
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(SolicitudDB, id_solicitud)
        return _mapear_db_a_be(db_obj) if db_obj else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener solicitud por id: {e}")
    finally:
        sesion.close()


def listar_solicitudes(limit: int = 50, offset: int = 0) -> List[SolicitudBE]:
    """
    Lista solicitudes con paginación, ordenadas por fecha más reciente.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(SolicitudDB).order_by(SolicitudDB.fechaHora.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al listar solicitudes: {e}")
    finally:
        sesion.close()


def obtener_solicitudes_por_solicitante(id_solicitante: int, limit: int = 50, offset: int = 0) -> List[SolicitudBE]:
    """
    Obtiene todas las solicitudes de un solicitante específico.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(SolicitudDB).filter(
            SolicitudDB.solicitante_id == id_solicitante
        ).order_by(SolicitudDB.fechaHora.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener solicitudes por solicitante: {e}")
    finally:
        sesion.close()


def actualizar_solicitud(id_solicitud: int, cambios: dict) -> Optional[SolicitudBE]:
    """
    Actualiza campos de la solicitud. `cambios` puede incluir:
    solicitante_id, ubicacion_id, fechaHora.
    """
    if not cambios:
        raise ValueError("No hay cambios para aplicar")

    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(SolicitudDB, id_solicitud)
        if not db_obj:
            return None

        # Validar que las FKs existan si se están actualizando
        if "solicitante_id" in cambios:
            solicitante = obtener_solicitante_por_id(cambios["solicitante_id"])
            if not solicitante:
                raise ValueError(f"Solicitante con id {cambios['solicitante_id']} no existe")
        
        if "ubicacion_id" in cambios:
            ubicacion = obtener_ubicacion_por_id(cambios["ubicacion_id"])
            if not ubicacion:
                raise ValueError(f"Ubicación con id {cambios['ubicacion_id']} no existe")

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
        raise RuntimeError(f"Error al actualizar solicitud: {e}")
    finally:
        sesion.close()


def eliminar_solicitud(id_solicitud: int) -> bool:
    """
    Elimina una solicitud por su ID.
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(SolicitudDB, id_solicitud)
        if not db_obj:
            return False
        sesion.delete(db_obj)
        sesion.commit()
        return True
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al eliminar solicitud: {e}")
    finally:
        sesion.close()

