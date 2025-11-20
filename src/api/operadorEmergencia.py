from fastapi import APIRouter, HTTPException, status, Body, Query, Path, Depends
from typing import List, Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import date

from src.businessLayer.businessEntities.operadorEmergencia import OperadorEmergencia
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento
from src.businessLayer.businessComponents.entidades.servicioOperadorEmergencia import (
    ServicioOperadorEmergencia,
)
from src.api.security import require_auth

operadores_emergencia_router = APIRouter(
    prefix="/operadores-emergencia",
    tags=["operadores-emergencia"],
    dependencies=[Depends(require_auth)],
)


class OperadorEmergenciaCreate(BaseModel):
    """Modelo de request para crear un operador de emergencia (sin id ni disponibilidad)."""
    nombre: str = Field(..., min_length=1)
    apellido: str = Field(..., min_length=1)
    fechaNacimiento: date
    tipoDocumento: TipoDocumento
    numeroDocumento: str = Field(..., min_length=1)
    nombre2: Optional[str] = None
    apellido2: Optional[str] = None
    turno: str = Field(..., min_length=1)


@operadores_emergencia_router.post(
    "",
    response_model=OperadorEmergencia,
    status_code=status.HTTP_201_CREATED,
    summary="Crear operador de emergencia",
    description="Crea un nuevo operador de emergencia y retorna el recurso creado con su ID asignado.",
)
def crear_operador(operador_data: OperadorEmergenciaCreate = Body(...)):
    try:
        # Convertir el modelo de request a OperadorEmergencia (sin id, disponibilidad por defecto False)
        operador = OperadorEmergencia(
            id=None,
            nombre=operador_data.nombre,
            apellido=operador_data.apellido,
            fechaNacimiento=operador_data.fechaNacimiento,
            tipoDocumento=operador_data.tipoDocumento,
            numeroDocumento=operador_data.numeroDocumento,
            nombre2=operador_data.nombre2,
            apellido2=operador_data.apellido2,
            disponibilidad=False,
            turno=operador_data.turno,
        )
        creado = ServicioOperadorEmergencia.crear(operador)
        if creado is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un operador con el mismo tipo y número de documento",
            )
        return creado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@operadores_emergencia_router.get(
    "/{id_operador}",
    response_model=OperadorEmergencia,
    summary="Obtener operador por ID",
)
def obtener_operador(
    id_operador: int = Path(..., gt=0, description="ID del operador"),
):
    try:
        encontrado = ServicioOperadorEmergencia.obtener_por_id(id_operador)
        if not encontrado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operador no encontrado")
        return encontrado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@operadores_emergencia_router.get(
    "",
    response_model=List[OperadorEmergencia],
    summary="Listar operadores de emergencia",
)
def listar_operadores(
    limit: int = Query(50, gt=0, le=200, description="Cantidad máxima de registros"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
):
    try:
        return ServicioOperadorEmergencia.listar(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@operadores_emergencia_router.put(
    "/{id_operador}",
    response_model=OperadorEmergencia,
    summary="Actualizar operador de emergencia",
    description="Actualiza campos del operador y retorna el recurso actualizado.",
)
def actualizar_operador(
    id_operador: int = Path(..., gt=0, description="ID del operador"),
    cambios: Dict[str, Any] = Body(..., description="Campos a actualizar"),
):
    try:
        actualizado = ServicioOperadorEmergencia.actualizar(id_operador, cambios)
        if not actualizado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operador no encontrado o conflicto de datos")
        return actualizado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@operadores_emergencia_router.delete(
    "/{id_operador}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar operador de emergencia",
    description="Elimina un operador por ID. No retorna contenido.",
)
def eliminar_operador(
    id_operador: int = Path(..., gt=0, description="ID del operador"),
):
    try:
        ok = ServicioOperadorEmergencia.eliminar(id_operador)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operador no encontrado")
        return None
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

