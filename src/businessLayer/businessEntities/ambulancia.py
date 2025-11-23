from pydantic import BaseModel
from typing import Optional
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
from src.businessLayer.businessEntities.ubicacion import Ubicacion
class Ambulancia(BaseModel):
    id: Optional[int] = None
    disponibilidad: bool = False
    placa: str
    tipoAmbulancia: TipoAmbulancia
    ubicacion: Optional[Ubicacion] = None
    id_operador_ambulancia: Optional[int] = None

    # Analizadores (Getters)
    def get_id(self) -> Optional[int]:
        """Retorna el ID de la ambulancia."""
        return self.id
    
    def get_disponibilidad(self) -> bool:
        """Retorna la disponibilidad de la ambulancia."""
        return self.disponibilidad
    
    def get_placa(self) -> str:
        """Retorna la placa de la ambulancia."""
        return self.placa

    #modificadores (Setters)
    def set_disponibilidad(self, disponibilidad: bool) -> None:
        """Establece la disponibilidad de la ambulancia."""
        self.disponibilidad = disponibilidad
    
    def set_placa(self, placa: str) -> None:
        """Establece la placa de la ambulancia."""
        self.placa = placa
    
    def set_tipo_ambulancia(self, tipoAmbulancia: TipoAmbulancia) -> None:
        """Establece el tipo de ambulancia."""
        self.tipoAmbulancia = tipoAmbulancia
    
    def set_ubicacion(self, ubicacion: Ubicacion) -> None:
        """Establece la ubicación de la ambulancia."""
        self.ubicacion = ubicacion
    
    def get_id_operador_ambulancia(self) -> Optional[int]:
        """Retorna el ID del operador de ambulancia."""
        return self.id_operador_ambulancia
    
    def set_id_operador_ambulancia(self, id_operador_ambulancia: Optional[int]) -> None:
        """Establece el ID del operador de ambulancia."""
        self.id_operador_ambulancia = id_operador_ambulancia
    
    #Método toString
    def __str__(self) -> str:
        return (f"Ambulancia(id={self.id}, "
                f"disponibilidad={self.disponibilidad}, "
                f"placa={self.placa}, "
                f"tipoAmbulancia={self.tipoAmbulancia}, "
                f"ubicacion={self.ubicacion}, "
                f"id_operador_ambulancia={self.id_operador_ambulancia})")