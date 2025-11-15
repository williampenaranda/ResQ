from fastapi import APIRouter, HTTPException, status, Body, Query, Path, Depends
from typing import List, Any, Dict, Optional

from src.businessLayer.businessEntities.operadorAmbulancia import OperadorAmbulancia
from src.businessLayer.businessComponents.actores.servicioOperadorAmbulancia import (
    ServicioOperadorAmbulancia,
)
from src.api.security import require_auth

operadores_ambulancia_router = APIRouter(
    prefix="/operadores-ambulancia",
    tags=["operadores-ambulancia"],
    dependencies=[Depends(require_auth)],
)


@operadores_ambulancia_router.post(
    "",
    response_model=OperadorAmbulancia,
    status_code=status.HTTP_201_CREATED,
    summary="Crear operador de ambulancia",
    description="Crea un nuevo operador de ambulancia y retorna el recurso creado con su ID asignado.",
)
def crear_operador(operador: OperadorAmbulancia = Body(...)):
    try:
        creado = ServicioOperadorAmbulancia.crear(operador)
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


@operadores_ambulancia_router.get(
    "/{id_operador}",
    response_model=OperadorAmbulancia,
    summary="Obtener operador por ID",
)
def obtener_operador(
    id_operador: int = Path(..., gt=0, description="ID del operador"),
):
    try:
        encontrado = ServicioOperadorAmbulancia.obtener_por_id(id_operador)
        if not encontrado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operador no encontrado")
        return encontrado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@operadores_ambulancia_router.get(
    "",
    response_model=List[OperadorAmbulancia],
    summary="Listar operadores de ambulancia",
)
def listar_operadores(
    limit: int = Query(50, gt=0, le=200, description="Cantidad máxima de registros"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
):
    try:
        return ServicioOperadorAmbulancia.listar(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@operadores_ambulancia_router.put(
    "/{id_operador}",
    response_model=OperadorAmbulancia,
    summary="Actualizar operador de ambulancia",
    description="Actualiza campos del operador y retorna el recurso actualizado.",
)
def actualizar_operador(
    id_operador: int = Path(..., gt=0, description="ID del operador"),
    cambios: Dict[str, Any] = Body(..., description="Campos a actualizar"),
):
    try:
        actualizado = ServicioOperadorAmbulancia.actualizar(id_operador, cambios)
        if not actualizado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operador no encontrado o conflicto de datos")
        return actualizado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@operadores_ambulancia_router.delete(
    "/{id_operador}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar operador de ambulancia",
    description="Elimina un operador por ID. No retorna contenido.",
)
def eliminar_operador(
    id_operador: int = Path(..., gt=0, description="ID del operador"),
):
    try:
        ok = ServicioOperadorAmbulancia.eliminar(id_operador)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operador no encontrado")
        return None
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

