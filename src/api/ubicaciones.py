from fastapi import APIRouter, HTTPException, status, Body, Query, Path, Depends
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from src.businessLayer.businessEntities.ubicacion import Ubicacion
from src.businessLayer.businessComponents.actores.servicioUbicacion import (
    ServicioUbicacion,
)
from src.api.security import require_auth

ubicaciones_router = APIRouter(
    prefix="/ubicaciones",
    tags=["ubicaciones"]
    # dependencies=[Depends(require_auth)]
)


class UbicacionCreate(BaseModel):
    """Modelo para crear una ubicación sin ID (se genera automáticamente)"""
    latitud: float = Field(..., ge=-90.0, le=90.0, description="Latitud GPS")
    longitud: float = Field(..., ge=-180.0, le=180.0, description="Longitud GPS")
    fechaHora: datetime = Field(..., description="Fecha y hora de la ubicación")


@ubicaciones_router.post(
    "",
    response_model=Ubicacion,
    status_code=status.HTTP_201_CREATED,
    summary="Crear ubicación",
    description="Crea una nueva ubicación y retorna la ubicación creada con su ID asignado automáticamente. El ID se genera en la base de datos.",
)
def crear_ubicacion(ubicacion: UbicacionCreate = Body(...)):
    try:
        # Convertir el modelo de request a la entidad de negocio sin ID
        ubicacion_be = Ubicacion(
            id=None,  # El ID se genera automáticamente
            latitud=ubicacion.latitud,
            longitud=ubicacion.longitud,
            fechaHora=ubicacion.fechaHora
        )
        creada = ServicioUbicacion.crear(ubicacion_be)
        if creada is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error al crear la ubicación",
            )
        return creada
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@ubicaciones_router.get(
    "/{id_ubicacion}",
    response_model=Ubicacion,
    summary="Obtener ubicación por ID",
    description="Obtiene una ubicación por su identificador único.",
)
def obtener_ubicacion(
    id_ubicacion: int = Path(..., gt=0, description="ID de la ubicación"),
):
    try:
        encontrada = ServicioUbicacion.obtener_por_id(id_ubicacion)
        if not encontrada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicación no encontrada")
        return encontrada
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@ubicaciones_router.get(
    "",
    response_model=List[Ubicacion],
    summary="Listar ubicaciones",
    description="Lista todas las ubicaciones con paginación.",
)
def listar_ubicaciones(
    limit: int = Query(50, gt=0, le=200, description="Cantidad máxima de registros"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
):
    try:
        return ServicioUbicacion.listar(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@ubicaciones_router.put(
    "/{id_ubicacion}",
    response_model=Ubicacion,
    summary="Actualizar ubicación",
    description="Actualiza campos de la ubicación y retorna la ubicación actualizada.",
)
def actualizar_ubicacion(
    id_ubicacion: int = Path(..., gt=0, description="ID de la ubicación"),
    cambios: Dict[str, Any] = Body(..., description="Campos a actualizar (latitud, longitud, fechaHora)"),
):
    try:
        actualizada = ServicioUbicacion.actualizar(id_ubicacion, cambios)
        if not actualizada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicación no encontrada o conflicto de datos")
        return actualizada
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@ubicaciones_router.delete(
    "/{id_ubicacion}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ubicación",
    description="Elimina una ubicación por ID. No retorna contenido.",
)
def eliminar_ubicacion(
    id_ubicacion: int = Path(..., gt=0, description="ID de la ubicación"),
):
    try:
        ok = ServicioUbicacion.eliminar(id_ubicacion)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicación no encontrada")
        return None
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

