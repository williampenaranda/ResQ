"""
Repositorio de acceso a datos para Ambulancias.

Proporciona operaciones CRUD usando SQLAlchemy y mapea hacia/desde
la entidad Pydantic `Ambulancia` de la capa de negocio.
"""

from typing import List, Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.dataLayer.bd import SessionLocal
from src.dataLayer.models.modeloAmbulancia import Ambulancia as AmbulanciaDB
from src.businessLayer.businessEntities.ambulancia import Ambulancia as AmbulanciaBE
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
from src.dataLayer.dataAccesComponets.repositorioUbicacion import obtener_ubicacion_por_id


# ========================= Helpers de mapeo =========================

def _mapear_be_a_db(ambulancia: AmbulanciaBE) -> AmbulanciaDB:
    """
    Mapea una Ambulancia de la capa de negocio a la capa de datos.
    Si la ubicación existe y tiene ID, se asigna. Si no, se deja como None.
    """
    ubicacion_id = None
    if ambulancia.ubicacion and ambulancia.ubicacion.id:
        ubicacion_id = ambulancia.ubicacion.id
    
    return AmbulanciaDB(
        disponibilidad=ambulancia.get_disponibilidad(),
        placa=ambulancia.get_placa(),
        tipoAmbulancia=ambulancia.tipoAmbulancia,
        ubicacion_id=ubicacion_id,
        id_operador_ambulancia=ambulancia.get_id_operador_ambulancia()
    )


def _mapear_db_a_be(db_obj: AmbulanciaDB) -> AmbulanciaBE:
    """
    Mapea una Ambulancia de la capa de datos a la capa de negocio.
    Carga el objeto completo de Ubicacion desde su repositorio si existe.
    """
    # Cargar la ubicación completa si existe
    ubicacion = None
    if db_obj.ubicacion_id:
        ubicacion = obtener_ubicacion_por_id(db_obj.ubicacion_id)
        if not ubicacion:
            raise RuntimeError(f"Ubicación con id {db_obj.ubicacion_id} no encontrada")
    
    # Crear la ambulancia con la ubicación (puede ser None)
    ambulancia = AmbulanciaBE(
        id=db_obj.id,
        disponibilidad=db_obj.disponibilidad,
        placa=db_obj.placa,
        tipoAmbulancia=TipoAmbulancia(db_obj.tipoAmbulancia) if isinstance(db_obj.tipoAmbulancia, str) else db_obj.tipoAmbulancia,
        ubicacion=ubicacion,
        id_operador_ambulancia=db_obj.id_operador_ambulancia
    )
    
    return ambulancia


# ========================= Operaciones CRUD =========================

def crear_ambulancia(ambulancia: AmbulanciaBE) -> Optional[AmbulanciaBE]:
    """
    Crea una ambulancia. Devuelve el modelo Pydantic con el id asignado.
    Retorna None en caso de error de integridad (FK inválida o placa duplicada).
    """
    if not isinstance(ambulancia, AmbulanciaBE):
        raise ValueError("El parámetro debe ser una instancia de Ambulancia")

    sesion: Session = SessionLocal()
    try:
        db_obj = _mapear_be_a_db(ambulancia)
        sesion.add(db_obj)
        sesion.commit()
        sesion.refresh(db_obj)
        return _mapear_db_a_be(db_obj)
    except IntegrityError:
        sesion.rollback()
        return None
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al crear ambulancia: {e}")
    finally:
        sesion.close()


def obtener_ambulancia_por_id(id_ambulancia: int) -> Optional[AmbulanciaBE]:
    """
    Obtiene una ambulancia por su ID.
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(AmbulanciaDB, id_ambulancia)
        return _mapear_db_a_be(db_obj) if db_obj else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener ambulancia por id: {e}")
    finally:
        sesion.close()


def obtener_ambulancia_por_placa(placa: str) -> Optional[AmbulanciaBE]:
    """
    Obtiene una ambulancia por su placa.
    """
    if not placa or not placa.strip():
        raise ValueError("La placa es requerida")
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.query(AmbulanciaDB).filter(
            AmbulanciaDB.placa == placa.strip()
        ).first()
        return _mapear_db_a_be(db_obj) if db_obj else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener ambulancia por placa: {e}")
    finally:
        sesion.close()


def listar_ambulancias(limit: int = 50, offset: int = 0) -> List[AmbulanciaBE]:
    """
    Lista ambulancias con paginación.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(AmbulanciaDB).order_by(AmbulanciaDB.id.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al listar ambulancias: {e}")
    finally:
        sesion.close()


def listar_ambulancias_disponibles(limit: int = 50, offset: int = 0) -> List[AmbulanciaBE]:
    """
    Lista ambulancias disponibles con paginación.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(AmbulanciaDB).filter(
            AmbulanciaDB.disponibilidad == True
        ).order_by(AmbulanciaDB.id.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al listar ambulancias disponibles: {e}")
    finally:
        sesion.close()


def listar_ambulancias_por_tipo(tipo: TipoAmbulancia, limit: int = 50, offset: int = 0) -> List[AmbulanciaBE]:
    """
    Lista ambulancias por tipo con paginación.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(AmbulanciaDB).filter(
            AmbulanciaDB.tipoAmbulancia == tipo
        ).order_by(AmbulanciaDB.id.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al listar ambulancias por tipo: {e}")
    finally:
        sesion.close()


def actualizar_ambulancia(id_ambulancia: int, cambios: dict) -> Optional[AmbulanciaBE]:
    """
    Actualiza campos de la ambulancia. `cambios` puede incluir:
    disponibilidad, placa, tipoAmbulancia, ubicacion_id.
    """
    if not cambios:
        raise ValueError("No hay cambios para aplicar")

    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(AmbulanciaDB, id_ambulancia)
        if not db_obj:
            return None

        # Validar que la FK exista si se está actualizando
        if "ubicacion_id" in cambios:
            ubicacion = obtener_ubicacion_por_id(cambios["ubicacion_id"])
            if not ubicacion:
                raise ValueError(f"Ubicación con id {cambios['ubicacion_id']} no existe")

        # Convertir enum si es necesario
        if "tipoAmbulancia" in cambios and isinstance(cambios["tipoAmbulancia"], str):
            cambios["tipoAmbulancia"] = TipoAmbulancia(cambios["tipoAmbulancia"])

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
        raise RuntimeError(f"Error al actualizar ambulancia: {e}")
    finally:
        sesion.close()


def eliminar_ambulancia(id_ambulancia: int) -> bool:
    """
    Elimina una ambulancia por su ID.
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(AmbulanciaDB, id_ambulancia)
        if not db_obj:
            return False
        sesion.delete(db_obj)
        sesion.commit()
        return True
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al eliminar ambulancia: {e}")
    finally:
        sesion.close()


def obtener_ambulancia_por_operador(id_operador_ambulancia: int) -> Optional[AmbulanciaBE]:
    """
    Obtiene la ambulancia asignada a un operador de ambulancia.
    
    Args:
        id_operador_ambulancia: ID del operador de ambulancia
        
    Returns:
        Ambulancia asignada al operador o None si no se encuentra
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.query(AmbulanciaDB).filter(
            AmbulanciaDB.id_operador_ambulancia == id_operador_ambulancia
        ).first()
        return _mapear_db_a_be(db_obj) if db_obj else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener ambulancia por operador: {e}")
    finally:
        sesion.close()


def vincular_operador_ambulancia(id_ambulancia: int, id_operador_ambulancia: int) -> Optional[AmbulanciaBE]:
    """
    Vincula un operador de ambulancia con una ambulancia.
    
    Args:
        id_ambulancia: ID de la ambulancia
        id_operador_ambulancia: ID del operador de ambulancia a vincular
        
    Returns:
        Ambulancia actualizada o None si no se encuentra
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(AmbulanciaDB, id_ambulancia)
        if not db_obj:
            return None
        
        # Validar que el operador de ambulancia exista
        from src.dataLayer.dataAccesComponets.repositorioOperadorAmbulancia import obtener_operador_por_id
        operador = obtener_operador_por_id(id_operador_ambulancia)
        if not operador:
            raise ValueError(f"Operador de ambulancia con id {id_operador_ambulancia} no encontrado")
        
        # Actualizar el id_operador_ambulancia
        db_obj.id_operador_ambulancia = id_operador_ambulancia
        sesion.commit()
        sesion.refresh(db_obj)
        return _mapear_db_a_be(db_obj)
    except ValueError:
        sesion.rollback()
        raise
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al vincular operador de ambulancia: {e}")
    finally:
        sesion.close()

