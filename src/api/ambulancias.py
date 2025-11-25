from fastapi import APIRouter, HTTPException, status, Body, Query, Path
from typing import List, Any, Dict, Optional
from pydantic import BaseModel, Field
from src.businessLayer.businessEntities.ambulancia import Ambulancia
from src.businessLayer.businessComponents.entidades.servicioAmbulancia import (
    ServicioAmbulancia,
)
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia

ambulancias_router = APIRouter(
    prefix="/ambulancias",
    tags=["ambulancias"],
)

class AmbulanciaCreate(BaseModel):
    """Modelo de request para crear una ambulancia."""
    placa: str = Field(..., min_length=1, description="Placa de la ambulancia")
    tipoAmbulancia: TipoAmbulancia = Field(..., description="Tipo de ambulancia")

@ambulancias_router.post(
    "",
    response_model=Ambulancia,
    status_code=status.HTTP_201_CREATED,
    summary="Crear ambulancia",
    description="Crea una nueva ambulancia y retorna la ambulancia creada con su ID asignado.",
)
def crear_ambulancia(ambulancia_data: AmbulanciaCreate = Body(...)):
    try:
        ambulancia = Ambulancia(
            id=None,
            placa=ambulancia_data.placa,
            tipoAmbulancia=ambulancia_data.tipoAmbulancia,
            disponibilidad=False,
            ubicacion=None
        )
        creado = ServicioAmbulancia.crear(ambulancia)
        if creado is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Error al crear la ambulancia")
        return creado
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@ambulancias_router.get(
    "",
    response_model=List[Ambulancia],
    summary="Listar ambulancias",
    description="Lista todas las ambulancias con paginación.",
)
def listar_ambulancias(
    limit: int = Query(50, gt=0, le=200, description="Cantidad máxima de registros"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
):
    try:
        return ServicioAmbulancia.listar(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@ambulancias_router.get(
    "/{id_ambulancia}",
    response_model=Ambulancia,
    summary="Obtener ambulancia por ID",
    description="Obtiene una ambulancia por su ID.",
)
def obtener_ambulancia(id_ambulancia: int = Path(..., gt=0, description="ID de la ambulancia")):
    try:
        ambulancia = ServicioAmbulancia.obtener_por_id(id_ambulancia)
        if ambulancia is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ambulancia no encontrada")
        return ambulancia
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@ambulancias_router.put(
    "/{id_ambulancia}",
    response_model=Ambulancia,
    summary="Actualizar ambulancia",
    description="Actualiza una ambulancia existente.",
)
def actualizar_ambulancia(
    id_ambulancia: int = Path(..., gt=0, description="ID de la ambulancia"), 
    cambios: Dict[str, Any] = Body(..., description="Campos a actualizar"),
):
    try:
        ambulancia = ServicioAmbulancia.actualizar(id_ambulancia, cambios)
        if ambulancia is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ambulancia no encontrada o conflicto de datos")
        return ambulancia
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@ambulancias_router.delete(
    "/{id_ambulancia}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ambulancia",
    description="Elimina una ambulancia por ID. No retorna contenido.",
)
def eliminar_ambulancia(id_ambulancia: int = Path(..., gt=0, description="ID de la ambulancia")):
    try:
        ok = ServicioAmbulancia.eliminar(id_ambulancia)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ambulancia no encontrada")
        return None
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


class VincularOperadorRequest(BaseModel):
    """Modelo de request para vincular un operador de ambulancia."""
    id_operador_ambulancia: int = Field(..., gt=0, description="ID del operador de ambulancia a vincular")


class VincularOperadorPorPlacaRequest(BaseModel):
    """Modelo de request para vincular un operador de ambulancia usando la placa."""
    id_operador_ambulancia: int = Field(..., gt=0, description="ID del operador de ambulancia a vincular")
    placa: str = Field(..., min_length=1, description="Placa de la ambulancia")


@ambulancias_router.put(
    "/vincular-operador-por-placa",
    response_model=Ambulancia,
    summary="Vincular operador de ambulancia por placa",
    description="Vincula un operador de ambulancia con una ambulancia usando la placa de la ambulancia.",
)
def vincular_operador_por_placa(
    request: VincularOperadorPorPlacaRequest = Body(...)
):
    try:
        # Buscar la ambulancia por placa
        ambulancia = ServicioAmbulancia.obtener_por_placa(request.placa)
        if ambulancia is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ambulancia con placa '{request.placa}' no encontrada"
            )
        
        # Vincular el operador
        from src.dataLayer.dataAccesComponets.repositorioAmbulancia import vincular_operador_ambulancia as repo_vincular
        ambulancia_actualizada = repo_vincular(ambulancia.id, request.id_operador_ambulancia)
        if ambulancia_actualizada is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ambulancia no encontrada")
        
        return ambulancia_actualizada
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@ambulancias_router.put(
    "/{id_ambulancia}/vincular-operador",
    response_model=Ambulancia,
    summary="Vincular operador de ambulancia",
    description="Vincula un operador de ambulancia con una ambulancia específica.",
)
def vincular_operador_ambulancia(
    id_ambulancia: int = Path(..., gt=0, description="ID de la ambulancia"),
    request: VincularOperadorRequest = Body(...)
):
    try:
        from src.dataLayer.dataAccesComponets.repositorioAmbulancia import vincular_operador_ambulancia as repo_vincular
        ambulancia = repo_vincular(id_ambulancia, request.id_operador_ambulancia)
        if ambulancia is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ambulancia no encontrada")
        return ambulancia
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))