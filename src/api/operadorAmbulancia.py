from fastapi import APIRouter, HTTPException, status, Body, Query, Path
from typing import List, Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import date

from src.businessLayer.businessEntities.operadorAmbulancia import OperadorAmbulancia
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento
from src.businessLayer.businessComponents.entidades.servicioOperadorAmbulancia import (
    ServicioOperadorAmbulancia,
)
operadores_ambulancia_router = APIRouter(
    prefix="/operadores-ambulancia",
    tags=["operadores-ambulancia"],
)


class OperadorAmbulanciaCreate(BaseModel):
    """Modelo de request para crear un operador de ambulancia (sin id ni disponibilidad)."""
    nombre: str = Field(..., min_length=1)
    apellido: str = Field(..., min_length=1)
    fechaNacimiento: date
    tipoDocumento: TipoDocumento
    numeroDocumento: str = Field(..., min_length=1)
    nombre2: Optional[str] = None
    apellido2: Optional[str] = None
    licencia: str = Field(..., min_length=1)


@operadores_ambulancia_router.post(
    "",
    response_model=OperadorAmbulancia,
    status_code=status.HTTP_201_CREATED,
    summary="Crear operador de ambulancia",
    description="Crea un nuevo operador de ambulancia y retorna el recurso creado con su ID asignado.",
)
def crear_operador(operador_data: OperadorAmbulanciaCreate = Body(...)):
    try:
        # Convertir el modelo de request a OperadorAmbulancia (sin id, disponibilidad por defecto False)
        operador = OperadorAmbulancia(
            id=None,
            nombre=operador_data.nombre,
            apellido=operador_data.apellido,
            fechaNacimiento=operador_data.fechaNacimiento,
            tipoDocumento=operador_data.tipoDocumento,
            numeroDocumento=operador_data.numeroDocumento,
            nombre2=operador_data.nombre2,
            apellido2=operador_data.apellido2,
            disponibilidad=False,
            licencia=operador_data.licencia,
        )
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

