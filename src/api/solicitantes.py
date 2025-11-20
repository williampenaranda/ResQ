from fastapi import APIRouter, HTTPException, status, Body, Query, Path, Depends
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import date
from src.businessLayer.businessEntities.solicitante import Solicitante
from src.businessLayer.businessComponents.entidades.servicioSolicitante import (
    ServicioSolicitante,
)
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento
from src.api.security import require_auth

solicitantes_router = APIRouter(
    prefix="/solicitantes",
    tags=["solicitantes"]
    # dependencies=[Depends(require_auth)]
)


class SolicitanteCreate(BaseModel):
    """Modelo de request para crear un solicitante (sin id)."""
    nombre: str = Field(..., min_length=1)
    apellido: str = Field(..., min_length=1)
    fechaNacimiento: date
    tipoDocumento: TipoDocumento
    numeroDocumento: str = Field(..., min_length=1)
    nombre2: Optional[str] = None
    apellido2: Optional[str] = None
    padecimientos: Optional[List[str]] = Field(default_factory=list)


@solicitantes_router.post(
    "",
    response_model=Solicitante,
    status_code=status.HTTP_201_CREATED,
    summary="Crear solicitante",
    description="Crea un nuevo solicitante y retorna el solicitante creado con su ID asignado.",
)
def crear_solicitante(solicitante_data: SolicitanteCreate = Body(...)):
    try:
        # Convertir el modelo de request a Solicitante (sin id, se asignará en la BD)
        solicitante = Solicitante(
            id=None,
            nombre=solicitante_data.nombre,
            apellido=solicitante_data.apellido,
            fechaNacimiento=solicitante_data.fechaNacimiento,
            tipoDocumento=solicitante_data.tipoDocumento,
            numeroDocumento=solicitante_data.numeroDocumento,
            nombre2=solicitante_data.nombre2,
            apellido2=solicitante_data.apellido2,
            padecimientos=solicitante_data.padecimientos,
        )
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
    "/buscar/documento",
    response_model=Solicitante,
    summary="Obtener solicitante por número de documento",
)
def obtener_solicitante_por_numero_documento(
    numero_documento: str = Query(..., description="Número de documento del solicitante"),
):
    try:
        encontrado = ServicioSolicitante.obtener_por_numero_documento(numero_documento)
        if not encontrado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitante no encontrado")
        return encontrado
    except HTTPException:
        # Re-lanzar HTTPException sin modificar (FastAPI la maneja automáticamente)
        raise
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re:
        # Errores de base de datos desde el repositorio
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(re))
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