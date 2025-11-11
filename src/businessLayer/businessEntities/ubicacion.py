from pydantic import BaseModel
from datetime import datetime

class Ubicacion(BaseModel):
    latitud: float
    longitud: float
    fechaHora: datetime