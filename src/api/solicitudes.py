from fastapi import APIRouter, HTTPException, status, Body, Query, Path, Depends
from typing import List, Optional, Any, Dict
from src.businessLayer.businessEntities.solicitud import Solicitud
from src.businessLayer.businessComponents.actores.servicioSolicitud import (
    ServicioSolicitud,
)
from src.api.security import require_auth

solicitudes_router = APIRouter(
    prefix="/solicitudes",
    tags=["solicitudes"]
    # dependencies=[Depends(require_auth)]
)


@solicitudes_router.post(
    "",
    response_model=Solicitud,
    status_code=status.HTTP_201_CREATED,
    summary="Crear solicitud",
    description="Crea una nueva solicitud y retorna la solicitud creada con su ID asignado. Requiere que el solicitante y ubicación ya existan en el sistema.",
)
def crear_solicitud(solicitud: Solicitud = Body(...)):
    try:
        creada = ServicioSolicitud.crear(solicitud)
        if creada is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error al crear la solicitud. Verifique que el solicitante y ubicación existan.",
            )
        return creada
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@solicitudes_router.get(
    "/{id_solicitud}",
    response_model=Solicitud,
    summary="Obtener solicitud por ID",
    description="Obtiene una solicitud por su identificador único.",
)
def obtener_solicitud(
    id_solicitud: int = Path(..., gt=0, description="ID de la solicitud"),
):
    try:
        encontrada = ServicioSolicitud.obtener_por_id(id_solicitud)
        if not encontrada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
        return encontrada
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@solicitudes_router.get(
    "",
    response_model=List[Solicitud],
    summary="Listar solicitudes",
    description="Lista todas las solicitudes con paginación, ordenadas por fecha más reciente.",
)
def listar_solicitudes(
    limit: int = Query(50, gt=0, le=200, description="Cantidad máxima de registros"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
):
    try:
        return ServicioSolicitud.listar(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@solicitudes_router.get(
    "/solicitante/{id_solicitante}",
    response_model=List[Solicitud],
    summary="Obtener solicitudes por solicitante",
    description="Obtiene todas las solicitudes de un solicitante específico.",
)
def obtener_solicitudes_por_solicitante(
    id_solicitante: int = Path(..., gt=0, description="ID del solicitante"),
    limit: int = Query(50, gt=0, le=200, description="Cantidad máxima de registros"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
):
    try:
        return ServicioSolicitud.obtener_por_solicitante(id_solicitante, limit=limit, offset=offset)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@solicitudes_router.put(
    "/{id_solicitud}",
    response_model=Solicitud,
    summary="Actualizar solicitud",
    description="Actualiza campos de la solicitud y retorna la solicitud actualizada. Puede actualizar solicitante_id, ubicacion_id o fechaHora.",
)
def actualizar_solicitud(
    id_solicitud: int = Path(..., gt=0, description="ID de la solicitud"),
    cambios: Dict[str, Any] = Body(..., description="Campos a actualizar (solicitante_id, ubicacion_id, fechaHora)"),
):
    try:
        actualizada = ServicioSolicitud.actualizar(id_solicitud, cambios)
        if not actualizada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada o conflicto de datos")
        return actualizada
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@solicitudes_router.delete(
    "/{id_solicitud}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar solicitud",
    description="Elimina una solicitud por ID. No retorna contenido.",
)
def eliminar_solicitud(
    id_solicitud: int = Path(..., gt=0, description="ID de la solicitud"),
):
    try:
        ok = ServicioSolicitud.eliminar(id_solicitud)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
        return None
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

