"""
Repositorio de acceso a datos para Órdenes de Despacho.

Proporciona operaciones CRUD usando SQLAlchemy y mapea hacia/desde
la entidad Pydantic `OrdenDespacho` de la capa de negocio.
"""

from typing import List, Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.dataLayer.bd import SessionLocal
from src.dataLayer.models.modeloOrdenDespacho import OrdenDespacho as OrdenDespachoDB
from src.businessLayer.businessEntities.ordenDespacho import OrdenDespacho as OrdenDespachoBE
from src.dataLayer.dataAccesComponets.repositorioEmergencias import obtener_emergencia_por_id
from src.dataLayer.dataAccesComponets.repositorioAmbulancia import obtener_ambulancia_por_id
from src.dataLayer.dataAccesComponets.repositorioOperadorAmbulancia import obtener_operador_por_id as obtener_operador_ambulancia_por_id
from src.dataLayer.dataAccesComponets.repositorioOperadorEmergencia import obtener_operador_por_id


# ========================= Helpers de mapeo =========================

def _mapear_be_a_db(orden_despacho: OrdenDespachoBE) -> OrdenDespachoDB:
    """
    Mapea una OrdenDespacho de la capa de negocio a la capa de datos.
    Requiere que la emergencia, ambulancia y operadores ya existan en la BD (tengan ID).
    """
    if not orden_despacho.emergencia.id:
        raise ValueError("La emergencia debe tener un ID para crear la orden de despacho")
    if not orden_despacho.ambulancia.id:
        raise ValueError("La ambulancia debe tener un ID para crear la orden de despacho")
    if not orden_despacho.operadorAmbulancia.id:
        raise ValueError("El operador de ambulancia debe tener un ID para crear la orden de despacho")
    if not orden_despacho.operadorEmergencia.id:
        raise ValueError("El operador de emergencia debe tener un ID para crear la orden de despacho")
    
    return OrdenDespachoDB(
        fechaHora=orden_despacho.fechaHora,
        emergencia_id=orden_despacho.emergencia.id,
        ambulancia_id=orden_despacho.ambulancia.id,
        operador_ambulancia_id=orden_despacho.operadorAmbulancia.id,
        operador_emergencia_id=orden_despacho.operadorEmergencia.id
    )


def _mapear_db_a_be(db_obj: OrdenDespachoDB) -> OrdenDespachoBE:
    """
    Mapea una OrdenDespacho de la capa de datos a la capa de negocio.
    Carga los objetos completos de Emergencia, Ambulancia y Operadores desde sus repositorios.
    """
    # Cargar la emergencia completa
    emergencia = obtener_emergencia_por_id(db_obj.emergencia_id)
    if not emergencia:
        raise RuntimeError(f"Emergencia con id {db_obj.emergencia_id} no encontrada")
    
    # Cargar la ambulancia completa
    ambulancia = obtener_ambulancia_por_id(db_obj.ambulancia_id)
    if not ambulancia:
        raise RuntimeError(f"Ambulancia con id {db_obj.ambulancia_id} no encontrada")
    
    # Cargar el operador de ambulancia completo
    operador_ambulancia = obtener_operador_ambulancia_por_id(db_obj.operador_ambulancia_id)
    if not operador_ambulancia:
        raise RuntimeError(f"Operador de ambulancia con id {db_obj.operador_ambulancia_id} no encontrado")
    
    # Cargar el operador de emergencia completo
    operador_emergencia = obtener_operador_por_id(db_obj.operador_emergencia_id)
    if not operador_emergencia:
        raise RuntimeError(f"Operador de emergencia con id {db_obj.operador_emergencia_id} no encontrado")
    
    return OrdenDespachoBE(
        id=db_obj.id,
        fechaHora=db_obj.fechaHora,
        emergencia=emergencia,
        ambulancia=ambulancia,
        operadorAmbulancia=operador_ambulancia,
        operadorEmergencia=operador_emergencia
    )


# ========================= Operaciones CRUD =========================

def crear_orden_despacho(orden_despacho: OrdenDespachoBE) -> Optional[OrdenDespachoBE]:
    """
    Crea una orden de despacho. Devuelve el modelo Pydantic con el id asignado.
    Retorna None en caso de error de integridad (FK inválida).
    """
    if not isinstance(orden_despacho, OrdenDespachoBE):
        raise ValueError("El parámetro debe ser una instancia de OrdenDespacho")

    sesion: Session = SessionLocal()
    try:
        db_obj = _mapear_be_a_db(orden_despacho)
        sesion.add(db_obj)
        sesion.commit()
        sesion.refresh(db_obj)
        return _mapear_db_a_be(db_obj)
    except IntegrityError:
        sesion.rollback()
        return None
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al crear orden de despacho: {e}")
    finally:
        sesion.close()


def obtener_orden_despacho_por_id(id_orden: int) -> Optional[OrdenDespachoBE]:
    """
    Obtiene una orden de despacho por su ID.
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(OrdenDespachoDB, id_orden)
        return _mapear_db_a_be(db_obj) if db_obj else None
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener orden de despacho por id: {e}")
    finally:
        sesion.close()


def listar_ordenes_despacho(limit: int = 50, offset: int = 0) -> List[OrdenDespachoBE]:
    """
    Lista órdenes de despacho con paginación, ordenadas por fecha de creación más reciente.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(OrdenDespachoDB).order_by(OrdenDespachoDB.fechaCreacion.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al listar órdenes de despacho: {e}")
    finally:
        sesion.close()


def obtener_ordenes_por_emergencia(id_emergencia: int, limit: int = 50, offset: int = 0) -> List[OrdenDespachoBE]:
    """
    Obtiene todas las órdenes de despacho asociadas a una emergencia específica.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(OrdenDespachoDB).filter(
            OrdenDespachoDB.emergencia_id == id_emergencia
        ).order_by(OrdenDespachoDB.fechaCreacion.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener órdenes por emergencia: {e}")
    finally:
        sesion.close()


def obtener_ordenes_por_ambulancia(id_ambulancia: int, limit: int = 50, offset: int = 0) -> List[OrdenDespachoBE]:
    """
    Obtiene todas las órdenes de despacho asignadas a una ambulancia específica.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(OrdenDespachoDB).filter(
            OrdenDespachoDB.ambulancia_id == id_ambulancia
        ).order_by(OrdenDespachoDB.fechaCreacion.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener órdenes por ambulancia: {e}")
    finally:
        sesion.close()


def obtener_ordenes_por_operador_ambulancia(id_operador: int, limit: int = 50, offset: int = 0) -> List[OrdenDespachoBE]:
    """
    Obtiene todas las órdenes de despacho asignadas a un operador de ambulancia específico.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(OrdenDespachoDB).filter(
            OrdenDespachoDB.operador_ambulancia_id == id_operador
        ).order_by(OrdenDespachoDB.fechaCreacion.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener órdenes por operador de ambulancia: {e}")
    finally:
        sesion.close()


def obtener_ordenes_por_operador_emergencia(id_operador: int, limit: int = 50, offset: int = 0) -> List[OrdenDespachoBE]:
    """
    Obtiene todas las órdenes de despacho creadas por un operador de emergencia específico.
    """
    sesion: Session = SessionLocal()
    try:
        query = sesion.query(OrdenDespachoDB).filter(
            OrdenDespachoDB.operador_emergencia_id == id_operador
        ).order_by(OrdenDespachoDB.fechaCreacion.desc()).offset(offset).limit(limit)
        return [_mapear_db_a_be(row) for row in query.all()]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error al obtener órdenes por operador de emergencia: {e}")
    finally:
        sesion.close()


def actualizar_orden_despacho(id_orden: int, cambios: dict) -> Optional[OrdenDespachoBE]:
    """
    Actualiza campos de la orden de despacho. `cambios` puede incluir:
    fechaHora, emergencia_id, ambulancia_id, operador_ambulancia_id, operador_emergencia_id.
    """
    if not cambios:
        raise ValueError("No hay cambios para aplicar")

    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(OrdenDespachoDB, id_orden)
        if not db_obj:
            return None

        # Validar que las FKs existan si se están actualizando
        if "emergencia_id" in cambios:
            emergencia = obtener_emergencia_por_id(cambios["emergencia_id"])
            if not emergencia:
                raise ValueError(f"Emergencia con id {cambios['emergencia_id']} no existe")
        
        if "ambulancia_id" in cambios:
            ambulancia = obtener_ambulancia_por_id(cambios["ambulancia_id"])
            if not ambulancia:
                raise ValueError(f"Ambulancia con id {cambios['ambulancia_id']} no existe")
        
        if "operador_ambulancia_id" in cambios:
            operador_ambulancia = obtener_operador_ambulancia_por_id(cambios["operador_ambulancia_id"])
            if not operador_ambulancia:
                raise ValueError(f"Operador de ambulancia con id {cambios['operador_ambulancia_id']} no existe")
        
        if "operador_emergencia_id" in cambios:
            operador_emergencia = obtener_operador_por_id(cambios["operador_emergencia_id"])
            if not operador_emergencia:
                raise ValueError(f"Operador de emergencia con id {cambios['operador_emergencia_id']} no existe")

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
        raise RuntimeError(f"Error al actualizar orden de despacho: {e}")
    finally:
        sesion.close()


def eliminar_orden_despacho(id_orden: int) -> bool:
    """
    Elimina una orden de despacho por su ID.
    """
    sesion: Session = SessionLocal()
    try:
        db_obj = sesion.get(OrdenDespachoDB, id_orden)
        if not db_obj:
            return False
        sesion.delete(db_obj)
        sesion.commit()
        return True
    except SQLAlchemyError as e:
        sesion.rollback()
        raise RuntimeError(f"Error al eliminar orden de despacho: {e}")
    finally:
        sesion.close()
