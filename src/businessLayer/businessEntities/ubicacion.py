from pydantic import BaseModel
from datetime import datetime

class Ubicacion(BaseModel):
    latitud: float
    longitud: float
    fechaHora: datetime

    # Analizadores (Getters)
    def get_latitud(self) -> float:
        """Retorna la latitud de la ubicación."""
        return self.latitud
    
    def get_longitud(self) -> float:
        """Retorna la longitud de la ubicación."""
        return self.longitud
    
    def get_fecha_hora(self) -> datetime:
        """Retorna la fecha y hora de la ubicación."""
        return self.fechaHora

    # Modificadores (Setters)
    def set_latitud(self, latitud: float) -> None:
        """Establece la latitud de la ubicación."""
        if latitud is None:
            raise ValueError("La latitud no puede ser None")
        if not isinstance(latitud, (int, float)):
            raise TypeError("La latitud debe ser un número")
        if latitud < -90 or latitud > 90:
            raise ValueError("La latitud debe estar entre -90 y 90 grados")
        self.latitud = float(latitud)
    
    def set_longitud(self, longitud: float) -> None:
        """Establece la longitud de la ubicación."""
        if longitud is None:
            raise ValueError("La longitud no puede ser None")
        if not isinstance(longitud, (int, float)):
            raise TypeError("La longitud debe ser un número")
        if longitud < -180 or longitud > 180:
            raise ValueError("La longitud debe estar entre -180 y 180 grados")
        self.longitud = float(longitud)
    
    def set_fecha_hora(self, fecha_hora: datetime) -> None:
        """Establece la fecha y hora de la ubicación."""
        if fecha_hora is None:
            raise ValueError("La fecha y hora no pueden ser None")
        if not isinstance(fecha_hora, datetime):
            raise TypeError("La fecha y hora deben ser una instancia de datetime")
        self.fechaHora = fecha_hora

    # Método toString
    def __str__(self) -> str:
        """Retorna una representación en cadena de la ubicación."""
        return f"Ubicacion(latitud={self.latitud}, longitud={self.longitud}, fechaHora={self.fechaHora})"
    