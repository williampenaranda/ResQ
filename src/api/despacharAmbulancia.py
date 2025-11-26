"""
Router para despachar ambulancias y emitir órdenes de despacho.
"""

from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel, Field
from src.businessLayer.businessEntities.ordenDespacho import OrdenDespacho
from src.businessLayer.businessWorkflow.emitirOrdenDespacho import EmitirOrdenDespacho

despachar_ambulancia_router = APIRouter(
    prefix="/despachar-ambulancia",
    tags=["despachar-ambulancia"],
)


class DespacharAmbulanciaRequest(BaseModel):
    """Modelo de request para despachar una ambulancia."""
    emergencia_id: int = Field(..., gt=0, description="ID de la emergencia a atender")
    ambulancia_id: int = Field(..., gt=0, description="ID de la ambulancia asignada")
    operador_ambulancia_id: int = Field(..., gt=0, description="ID del operador de ambulancia asignado")
    operador_emergencia_id: int = Field(..., gt=0, description="ID del operador de emergencia que emite la orden")


@despachar_ambulancia_router.post(
    "",
    response_model=OrdenDespacho,
    status_code=status.HTTP_201_CREATED,
    summary="Despachar ambulancia y emitir orden",
    description=(
        "Emite una orden de despacho asignando una ambulancia y operadores a una emergencia. "
        "Este endpoint valida la disponibilidad de la ambulancia y notifica al solicitante."
    ),
)
async def despachar_ambulancia(
    despacho_data: DespacharAmbulanciaRequest = Body(...)
):
    """
    Despacha una ambulancia para una emergencia.
    """
    try:
        print(f"[DEBUG] [DESPACHO] Recibida solicitud de despacho:")
        print(f"[DEBUG] [DESPACHO]   - emergencia_id: {despacho_data.emergencia_id}")
        print(f"[DEBUG] [DESPACHO]   - ambulancia_id: {despacho_data.ambulancia_id}")
        print(f"[DEBUG] [DESPACHO]   - operador_ambulancia_id: {despacho_data.operador_ambulancia_id}")
        print(f"[DEBUG] [DESPACHO]   - operador_emergencia_id: {despacho_data.operador_emergencia_id}")
        
        orden_creada = await EmitirOrdenDespacho.emitir_orden_despacho(
            emergencia_id=despacho_data.emergencia_id,
            ambulancia_id=despacho_data.ambulancia_id,
            operador_ambulancia_id=despacho_data.operador_ambulancia_id,
            operador_emergencia_id=despacho_data.operador_emergencia_id
        )
        return orden_creada
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
