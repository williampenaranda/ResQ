from pydantic import BaseModel
from datetime import datetime
from src.businessLayer.businessEntities.solicitante import Solicitante

class Emergencia(BaseModel):
    id: int
    solicitante: Solicitante
    fechaHora: datetime
    descripcion: str