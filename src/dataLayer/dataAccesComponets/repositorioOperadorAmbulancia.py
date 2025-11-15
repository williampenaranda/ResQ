"""
Repositorio de acceso a datos para Operadores de Ambulancia.

Proporciona operaciones CRUD usando SQLAlchemy y mapea hacia/desde
la entidad Pydantic `OperadorAmbulancia` de la capa de negocio.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.dataLayer.bd import SessionLocal
from src.dataLayer.models.modeloOperadorAmbulancia import OperadorAmbulancia as OperadorDB
from src.businessLayer.businessEntities.operadorAmbulancia import OperadorAmbulancia as OperadorBE
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento


# ========================= Helpers de mapeo =========================

def _mapear_be_a_db(operador: OperadorBE) -> OperadorDB:
    return OperadorDB(
        nombre=operador.nombre,
        nombre2=operador.nombre2,
        apellido=operador.apellido,
        apellido2=operador.apellido2,
        fechaNacimiento=operador.fechaNacimiento,
        tipoDocumento=operador.tipoDocumento,
        numeroDocumento=operador.numeroDocumento,
        disponibilidad=operador.disponibilidad,
        licencia=operador.licencia,
    )


def _mapear_db_a_be(db_obj: OperadorDB) -> OperadorBE:
    return OperadorBE(
        id=db_obj.id,
        nombre=db_obj.nombre,
        nombre2=db_obj.nombre2,
        apellido=db_obj.apellido,
        apellido2=db_obj.apellido2,
        fechaNacimiento=db_obj.fechaNacimiento,
        tipoDocumento=TipoDocumento(db_obj.tipoDocumento) if not isinstance(db_obj.tipoDocumento, TipoDocumento) else db_obj.tipoDocumento,
        numeroDocumento=db_obj.numeroDocumento,
        disponibilidad=db_obj.disponibilidad,
        licencia=db_obj.licencia,
    )


# ========================= Operaciones CRUD =========================

def crear_operador(operador: OperadorBE) -> Optional[OperadorBE]:
    """
    Crea un operador de ambulancia. Devuelve el modelo Pydantic con el id asignado.
    Retorna None en caso de conflicto de unicidad (documento duplicado).
    """
    if not isinstance(operador, OperadorBE):
        raise ValueError("El parámetro debe ser una instancia de OperadorAmbulancia")

    sesion: Session = SessionLocal()
    try:
        db_obj = _mapear_be_a_db(operador)
        sesion.add(db_obj)
        sesion.commit()
        sesion.refresh(db_obj)
        return _mapear_db_a_be(db_obj)
    except IntegrityError:
        sesion.rollback()
        return None
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al crear operador: {e}")
    finally:
        sesion.close()


def obtener_operador_por_id(id_operador: int) -> Optional[OperadorBE]:
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.query(OperadorDB).get(id_operador)
        return _mapear_db_a_be(db_obj) if db_obj else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener operador por id: {e}")
    finally:
        sesion.close()


def obtener_operador_por_documento(tipo: TipoDocumento, numero: str) -> Optional[OperadorBE]:
    if not numero or not numero.strip():
        raise ValueError("El número de documento es requerido")
    sesion: Session = SessionLocal()
    try:
        db_obj = (
            sesion.query(OperadorDB)
            .filter(OperadorDB.tipoDocumento == tipo, OperadorDB.numeroDocumento == numero.strip())
            .first()
        )
        return _mapear_db_a_be(db_obj) if db_obj else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener operador por documento: {e}")
    finally:
        sesion.close()


def listar_operadores(limit: int = 50, offset: int = 0) -> List[OperadorBE]:
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(OperadorDB).order_by(OperadorDB.id).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al listar operadores: {e}")
    finally:
        sesion.close()


def actualizar_operador(id_operador: int, cambios: Dict[str, Any]) -> Optional[OperadorBE]:
    if not cambios:
        raise ValueError("No hay cambios para aplicar")

    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.query(OperadorDB).get(id_operador)
        if not db_obj:
            return None

        for campo, valor in cambios.items():
            if campo == "tipoDocumento" and isinstance(valor, str):
                valor = TipoDocumento(valor)
            setattr(db_obj, campo, valor)

        sesion.commit()
        sesion.refresh(db_obj)
        return _mapear_db_a_be(db_obj)
    except IntegrityError:
        sesion.rollback()
        return None
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al actualizar operador: {e}")
    finally:
        sesion.close()


def eliminar_operador(id_operador: int) -> bool:
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.query(OperadorDB).get(id_operador)
        if not db_obj:
            return False
        sesion.delete(db_obj)
        sesion.commit()
        return True
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al eliminar operador: {e}")
    finally:
        sesion.close()

