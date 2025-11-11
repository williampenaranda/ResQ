from pydantic import BaseModel
from datetime import datetime
from src.businessLayer.businessEntities.solicitante import Solicitante
from src.businessLayer.businessEntities.ubicacion import Ubicacion
from src.businessLayer.businessEntities.enums.estadoEmergencia import EstadoEmergencia

class Emergencia(BaseModel):
    id: int
    solicitante: Solicitante
    fechaHora: datetime
    descripcion: str
    ubicacion: Ubicacion
    estado: EstadoEmergencia

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
    
    def get_descripcion(self) -> str:
        """Retorna la descripción de la emergencia."""
        return self.descripcion
    
    def get_ubicacion(self) -> Ubicacion:
        """Retorna la ubicación de la emergencia."""
        return self.ubicacion
    
    def get_estado(self) -> EstadoEmergencia:
        """Retorna el estado de la emergencia."""
        return self.estado

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
    
    def set_descripcion(self, descripcion: str) -> None:
        """Establece la descripción de la emergencia."""
        if descripcion is None:
            raise ValueError("La descripción no puede ser None")
        if not isinstance(descripcion, str):
            raise TypeError("La descripción debe ser una cadena de texto")
        descripcion_limpia = descripcion.strip()
        if not descripcion_limpia:
            raise ValueError("La descripción no puede estar vacía")
        self.descripcion = descripcion_limpia
    
    def set_ubicacion(self, ubicacion: Ubicacion) -> None:
        """Establece la ubicación de la emergencia."""
        if ubicacion is None:
            raise ValueError("La ubicación no puede ser None")
        if not isinstance(ubicacion, Ubicacion):
            raise TypeError("La ubicación debe ser una instancia de Ubicacion")
        self.ubicacion = ubicacion
    
    def set_estado(self, estado: EstadoEmergencia) -> None:
        """Establece el estado de la emergencia."""
        if estado is None:
            raise ValueError("El estado no puede ser None")
        if not isinstance(estado, EstadoEmergencia):
            raise TypeError("El estado debe ser una instancia de EstadoEmergencia")
        self.estado = estado

    # Método toString
    def __str__(self) -> str:
        """Retorna una representación en cadena de la emergencia."""
        descripcion_str = self.descripcion[:50] + "..." if len(self.descripcion) > 50 else self.descripcion
        return (f"Emergencia(id={self.id}, "
                f"estado={self.estado.value}, "
                f"fechaHora={self.fechaHora}, "
                f"descripcion='{descripcion_str}', "
                f"solicitante={self.solicitante.get_id()}, "
                f"ubicacion=({self.ubicacion.latitud}, {self.ubicacion.longitud}))")