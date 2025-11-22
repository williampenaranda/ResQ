from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.businessLayer.businessEntities.emergencia import Emergencia
from src.businessLayer.businessEntities.ambulancia import Ambulancia
from src.businessLayer.businessEntities.operadorAmbulancia import OperadorAmbulancia
from src.businessLayer.businessEntities.operadorEmergencia import OperadorEmergencia

class OrdenDespacho(BaseModel):
    id: Optional[int] = None
    fechaHora: datetime
    emergencia: Emergencia
    ambulancia: Ambulancia
    operadorAmbulancia: OperadorAmbulancia
    operadorEmergencia: OperadorEmergencia

    # Analizadores (Getters)
    def get_id(self) -> Optional[int]:
        """Retorna el ID de la orden de despacho."""
        return self.id
    
    def get_fecha_hora(self) -> datetime:
        """Retorna la fecha y hora de la orden de despacho."""
        return self.fechaHora
    
    def get_emergencia(self) -> Emergencia:
        """Retorna la emergencia asociada a la orden de despacho."""
        return self.emergencia
    
    def get_ambulancia(self) -> Ambulancia:
        """Retorna la ambulancia asignada a la orden de despacho."""
        return self.ambulancia
    
    def get_operador_ambulancia(self) -> OperadorAmbulancia:
        """Retorna el operador de ambulancia asignado."""
        return self.operadorAmbulancia
    
    def get_operador_emergencia(self) -> OperadorEmergencia:
        """Retorna el operador de emergencia que creó la orden."""
        return self.operadorEmergencia

    # Modificadores (Setters)
    
    def set_fecha_hora(self, fecha_hora: datetime) -> None:
        """Establece la fecha y hora de la orden de despacho."""
        if fecha_hora is None:
            raise ValueError("La fecha y hora no puede ser None")
        if not isinstance(fecha_hora, datetime):
            raise TypeError("La fecha y hora debe ser una instancia de datetime")
        self.fechaHora = fecha_hora
    
    def set_emergencia(self, emergencia: Emergencia) -> None:
        """Establece la emergencia asociada a la orden de despacho."""
        if emergencia is None:
            raise ValueError("La emergencia no puede ser None")
        if not isinstance(emergencia, Emergencia):
            raise TypeError("La emergencia debe ser una instancia de Emergencia")
        self.emergencia = emergencia
    
    def set_ambulancia(self, ambulancia: Ambulancia) -> None:
        """Establece la ambulancia asignada a la orden de despacho."""
        if ambulancia is None:
            raise ValueError("La ambulancia no puede ser None")
        if not isinstance(ambulancia, Ambulancia):
            raise TypeError("La ambulancia debe ser una instancia de Ambulancia")
        self.ambulancia = ambulancia
    
    def set_operador_ambulancia(self, operador_ambulancia: OperadorAmbulancia) -> None:
        """Establece el operador de ambulancia asignado."""
        if operador_ambulancia is None:
            raise ValueError("El operador de ambulancia no puede ser None")
        if not isinstance(operador_ambulancia, OperadorAmbulancia):
            raise TypeError("El operador de ambulancia debe ser una instancia de OperadorAmbulancia")
        self.operadorAmbulancia = operador_ambulancia
    
    def set_operador_emergencia(self, operador_emergencia: OperadorEmergencia) -> None:
        """Establece el operador de emergencia que creó la orden."""
        if operador_emergencia is None:
            raise ValueError("El operador de emergencia no puede ser None")
        if not isinstance(operador_emergencia, OperadorEmergencia):
            raise TypeError("El operador de emergencia debe ser una instancia de OperadorEmergencia")
        self.operadorEmergencia = operador_emergencia

    # Método toString
    def __str__(self) -> str:
        """Retorna una representación en cadena de la orden de despacho."""
        fecha_str = self.fechaHora.strftime("%Y-%m-%d %H:%M:%S")
        return (f"OrdenDespacho(id={self.id}, "
                f"fechaHora='{fecha_str}', "
                f"emergencia_id={self.emergencia.get_id()}, "
                f"ambulancia_id={self.ambulancia.get_id()}, "
                f"operadorAmbulancia_id={self.operadorAmbulancia.get_id()}, "
                f"operadorEmergencia_id={self.operadorEmergencia.get_id()})")
