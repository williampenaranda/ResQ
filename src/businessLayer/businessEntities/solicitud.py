from pydantic import BaseModel
from datetime import datetime
from src.businessLayer.businessEntities.solicitante import Solicitante
from src.businessLayer.businessEntities.ubicacion import Ubicacion
from src.businessLayer.businessEntities.enums.estadoEmergencia import EstadoEmergencia

class Solicitud(BaseModel):
    id: int
    solicitante: Solicitante
    fechaHora: datetime
    ubicacion: Ubicacion
    
    # Analizadores (Getters)
    def get_id(self) -> int:
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
    def set_id(self, id: int) -> None:
        """Establece el ID de la emergencia."""
        if id is None:
            raise ValueError("El ID no puede ser None")
        if not isinstance(id, int) or id < 0:
            raise ValueError("El ID debe ser un entero positivo")
        self.id = id
    
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