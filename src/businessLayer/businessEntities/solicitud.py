from pydantic import BaseModel
from datetime import datetime
from src.businessLayer.businessEntities.solicitante import Solicitante
from src.businessLayer.businessEntities.ubicacion import Ubicacion
from typing import Optional

class Solicitud(BaseModel):
    id: Optional[int] = None
    solicitante: Solicitante
    fechaHora: datetime
    ubicacion: Ubicacion
    
    # Analizadores (Getters)
    def get_id(self) -> Optional[int]:
        """Retorna el ID de la emergencia."""
        return self.id
    
    def get_solicitante(self) -> Solicitante:
        """Retorna el solicitante de la emergencia."""
        return self.solicitante
    
    def get_fecha_hora(self) -> datetime:
        """Retorna la fecha y hora de la emergencia."""
        return self.fechaHora
    
    def get_ubicacion(self) -> Ubicacion:
        """Retorna la ubicación de la emergencia."""
        return self.ubicacion
    
    # Modificadores (Setters)
    
    def set_solicitante(self, solicitante: Solicitante) -> None:
        """Establece el solicitante de la emergencia."""
        if solicitante is None:
            raise ValueError("El solicitante no puede ser None")
        if not isinstance(solicitante, Solicitante):
            raise TypeError("El solicitante debe ser una instancia de Solicitante")
        self.solicitante = solicitante
    
    def set_fecha_hora(self, fecha_hora: datetime) -> None:
        """Establece la fecha y hora de la emergencia."""
        if fecha_hora is None:
            raise ValueError("La fecha y hora no pueden ser None")
        if not isinstance(fecha_hora, datetime):
            raise TypeError("La fecha y hora deben ser una instancia de datetime")
        self.fechaHora = fecha_hora
    
    def set_ubicacion(self, ubicacion: Ubicacion) -> None:
        """Establece la ubicación de la emergencia."""
        if ubicacion is None:
            raise ValueError("La ubicación no puede ser None")
        if not isinstance(ubicacion, Ubicacion):
            raise TypeError("La ubicación debe ser una instancia de Ubicacion")
        self.ubicacion = ubicacion

    # Método toString
    def __str__(self) -> str:
        """Retorna una representación en cadena de la emergencia."""
        return (f"Emergencia(id={self.id}, "
                f"solicitante={self.solicitante.get_id()}, "
                f"ubicacion=({self.ubicacion.latitud}, {self.ubicacion.longitud}), "
                f"fechaHora={self.fechaHora})")