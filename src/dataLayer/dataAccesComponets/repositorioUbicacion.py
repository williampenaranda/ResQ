"""
Repositorio de acceso a datos para Ubicaciones.

Proporciona operaciones CRUD usando SQLAlchemy y mapea hacia/desde
la entidad Pydantic `Ubicacion` de la capa de negocio.
"""

from typing import List, Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.dataLayer.bd import SessionLocal
from src.dataLayer.models.modeloUbicacion import Ubicacion as UbicacionDB
from src.businessLayer.businessEntities.ubicacion import Ubicacion as UbicacionBE


# ========================= Helpers de mapeo =========================

def _mapear_be_a_db(ubicacion: UbicacionBE) -> UbicacionDB:
    return UbicacionDB(
        latitud=ubicacion.get_latitud(),
        longitud=ubicacion.get_longitud(),
        fechaHora=ubicacion.get_fecha_hora()
    )


def _mapear_db_a_be(db_obj: UbicacionDB) -> UbicacionBE:
    return UbicacionBE(
        id=db_obj.id,
        latitud=db_obj.latitud,
        longitud=db_obj.longitud,
        fechaHora=db_obj.fechaHora
    )


# ========================= Operaciones CRUD =========================

def crear_ubicacion(ubicacion: UbicacionBE) -> Optional[UbicacionBE]:
    """
    Crea una ubicación. Devuelve el modelo Pydantic con el id asignado.
    """
    if not isinstance(ubicacion, UbicacionBE):
        raise ValueError("El parámetro debe ser una instancia de Ubicacion")

    sesion: Session = SessionLocal()
    try:
        db_obj = _mapear_be_a_db(ubicacion)
        sesion.add(db_obj)
        sesion.commit()
        sesion.refresh(db_obj)
        return _mapear_db_a_be(db_obj)
    except IntegrityError:
        sesion.rollback()
        return None
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al crear ubicacion: {e}")
    finally:
        sesion.close()


def obtener_ubicacion_por_id(id_ubicacion: int) -> Optional[UbicacionBE]:
    """
    Obtiene una ubicación por su ID.
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(UbicacionDB, id_ubicacion)
        return _mapear_db_a_be(db_obj) if db_obj else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener ubicacion por id: {e}")
    finally:
        sesion.close()


def listar_ubicaciones(limit: int = 50, offset: int = 0) -> List[UbicacionBE]:
    """
    Lista ubicaciones con paginación.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(UbicacionDB).order_by(UbicacionDB.id.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al listar ubicaciones: {e}")
    finally:
        sesion.close()


def actualizar_ubicacion(id_ubicacion: int, cambios: dict) -> Optional[UbicacionBE]:
    """
    Actualiza campos de la ubicación. `cambios` puede incluir:
    latitud, longitud, fechaHora.
    """
    if not cambios:
        raise ValueError("No hay cambios para aplicar")

    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(UbicacionDB, id_ubicacion)
        if not db_obj:
            return None

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
        raise RuntimeError(f"Error al actualizar ubicacion: {e}")
    finally:
        sesion.close()


def eliminar_ubicacion(id_ubicacion: int) -> bool:
    """
    Elimina una ubicación por su ID.
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(UbicacionDB, id_ubicacion)
        if not db_obj:
            return False
        sesion.delete(db_obj)
        sesion.commit()
        return True
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al eliminar ubicacion: {e}")
    finally:
        sesion.close()