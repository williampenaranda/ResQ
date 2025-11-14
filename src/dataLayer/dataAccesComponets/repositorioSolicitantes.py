"""
Repositorio de acceso a datos para Solicitantes.

Proporciona operaciones CRUD usando SQLAlchemy y mapea hacia/desde
la entidad Pydantic `Solicitante` de la capa de negocio.
"""

from typing import List, Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.dataLayer.bd import SessionLocal
from src.dataLayer.models.modeloSolicitante import Solicitante as SolicitanteDB
from src.businessLayer.businessEntities.solicitante import Solicitante as SolicitanteBE
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento


# ========================= Helpers de mapeo =========================

def _mapear_be_a_db(solicitante: SolicitanteBE) -> SolicitanteDB:
    return SolicitanteDB(
        nombre=solicitante.nombre,
        nombre2=solicitante.nombre2,
        apellido=solicitante.apellido,
        apellido2=solicitante.apellido2,
        fechaNacimiento=solicitante.fechaNacimiento,
        tipoDocumento=solicitante.tipoDocumento,  # SAEnum acepta el Enum directamente
        numeroDocumento=solicitante.numeroDocumento,
        padecimientos=solicitante.get_padecimientos(),
    )


def _mapear_db_a_be(db_obj: SolicitanteDB) -> SolicitanteBE:
    return SolicitanteBE(
        id=db_obj.id,
        nombre=db_obj.nombre,
        nombre2=db_obj.nombre2,
        apellido=db_obj.apellido,
        apellido2=db_obj.apellido2,
        fechaNacimiento=db_obj.fechaNacimiento,
        tipoDocumento=TipoDocumento(db_obj.tipoDocumento) if not isinstance(db_obj.tipoDocumento, TipoDocumento) else db_obj.tipoDocumento,
        numeroDocumento=db_obj.numeroDocumento,
        padecimientos=db_obj.padecimientos or [],
    )


# ========================= Operaciones CRUD =========================

def crear_solicitante(solicitante: SolicitanteBE) -> Optional[SolicitanteBE]:
    """
    Crea un solicitante. Devuelve el modelo Pydantic con el id asignado.
    Retorna None en caso de conflicto de unicidad (documento duplicado).
    """
    if not isinstance(solicitante, SolicitanteBE):
        raise ValueError("El parámetro debe ser una instancia de Solicitante")

    sesion: Session = SessionLocal()
    try:
        db_obj = _mapear_be_a_db(solicitante)
        sesion.add(db_obj)
        sesion.commit()
        sesion.refresh(db_obj)
        return _mapear_db_a_be(db_obj)
    except IntegrityError:
        sesion.rollback()
        return None
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al crear solicitante: {e}")
    finally:
        sesion.close()


def obtener_solicitante_por_id(id_solicitante: int) -> Optional[SolicitanteBE]:
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.query(SolicitanteDB).get(id_solicitante)
        return _mapear_db_a_be(db_obj) if db_obj else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener solicitante por id: {e}")
    finally:
        sesion.close()


def obtener_solicitante_por_documento(numero: str, tipo: Optional[TipoDocumento] = None) -> Optional[SolicitanteBE]:
    """
    Obtiene un solicitante por número de documento.
    Si se proporciona el tipo, busca por ambos campos.
    Si solo se proporciona el número, busca solo por número (puede haber múltiples resultados, retorna el primero).
    """
    if not numero or not numero.strip():
        raise ValueError("El número de documento es requerido")
    sesion: Session = SessionLocal()
    try:
        # Normalizar el número de documento (eliminar espacios)
        numero_normalizado = numero.strip()
        # Primero intentar búsqueda directa (más eficiente)
        query = sesion.query(SolicitanteDB).filter(
            SolicitanteDB.numeroDocumento == numero_normalizado
        )
        if tipo is not None:
            query = query.filter(SolicitanteDB.tipoDocumento == tipo)
        db_obj = query.first()
        # Si no se encuentra, intentar con trim para manejar espacios en la BD
        if db_obj is None:
            query = sesion.query(SolicitanteDB).filter(
                func.trim(SolicitanteDB.numeroDocumento) == numero_normalizado
            )
            if tipo is not None:
                query = query.filter(SolicitanteDB.tipoDocumento == tipo)
            db_obj = query.first()
        return _mapear_db_a_be(db_obj) if db_obj else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener solicitante por documento: {e}")
    finally:
        sesion.close()


def listar_solicitantes(limit: int = 50, offset: int = 0) -> List[SolicitanteBE]:
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(SolicitanteDB).order_by(SolicitanteDB.id).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al listar solicitantes: {e}")
    finally:
        sesion.close()


def actualizar_solicitante(id_solicitante: int, cambios: dict) -> Optional[SolicitanteBE]:
    """
    Actualiza campos del solicitante. `cambios` puede incluir:
    nombre, nombre2, apellido, apellido2, fechaNacimiento,
    tipoDocumento (TipoDocumento), numeroDocumento, padecimientos (list[str]).
    """
    if not cambios:
        raise ValueError("No hay cambios para aplicar")

    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.query(SolicitanteDB).get(id_solicitante)
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
        raise RuntimeError(f"Error al actualizar solicitante: {e}")
    finally:
        sesion.close()


def eliminar_solicitante(id_solicitante: int) -> bool:
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.query(SolicitanteDB).get(id_solicitante)
        if not db_obj:
            return False
        sesion.delete(db_obj)
        sesion.commit()
        return True
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al eliminar solicitante: {e}")
    finally:
        sesion.close()

