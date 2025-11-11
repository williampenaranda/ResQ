from fastapi import APIRouter, HTTPException, status, Body, Query, Path
from typing import List, Optional, Any, Dict
from src.businessLayer.businessEntities.solicitante import Solicitante
from src.businessLayer.businessComponents.actores.servicioSolicitante import (
    ServicioSolicitante,
)
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento

solicitantes_router = APIRouter(
    prefix="/solicitantes",
    tags=["solicitantes"],
)


@solicitantes_router.post(
    "",
    response_model=Solicitante,
    status_code=status.HTTP_201_CREATED,
    summary="Crear solicitante",
    description="Crea un nuevo solicitante y retorna el solicitante creado con su ID asignado.",
)
def crear_solicitante(solicitante: Solicitante = Body(...)):
    try:
        creado = ServicioSolicitante.crear(solicitante)
        if creado is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un solicitante con el mismo tipo y número de documento",
            )
        return creado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@solicitantes_router.get(
    "/{id_solicitante}",
    response_model=Solicitante,
    summary="Obtener solicitante por ID",
)
def obtener_solicitante(
    id_solicitante: int = Path(..., gt=0, description="ID del solicitante"),
):
    try:
        encontrado = ServicioSolicitante.obtener_por_id(id_solicitante)
        if not encontrado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitante no encontrado")
        return encontrado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@solicitantes_router.get(
    "",
    response_model=List[Solicitante],
    summary="Listar solicitantes",
)
def listar_solicitantes(
    limit: int = Query(50, gt=0, le=200, description="Cantidad máxima de registros"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
):
    try:
        return ServicioSolicitante.listar(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@solicitantes_router.put(
    "/{id_solicitante}",
    response_model=Solicitante,
    summary="Actualizar solicitante",
    description="Actualiza campos del solicitante y retorna el solicitante actualizado.",
)
def actualizar_solicitante(
    id_solicitante: int = Path(..., gt=0, description="ID del solicitante"),
    cambios: Dict[str, Any] = Body(..., description="Campos a actualizar"),
):
    try:
        actualizado = ServicioSolicitante.actualizar(id_solicitante, cambios)
        if not actualizado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitante no encontrado o conflicto de datos")
        return actualizado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@solicitantes_router.delete(
    "/{id_solicitante}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar solicitante",
    description="Elimina un solicitante por ID. No retorna contenido.",
)
def eliminar_solicitante(
    id_solicitante: int = Path(..., gt=0, description="ID del solicitante"),
):
    try:
        ok = ServicioSolicitante.eliminar(id_solicitante)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitante no encontrado")
        return None
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))