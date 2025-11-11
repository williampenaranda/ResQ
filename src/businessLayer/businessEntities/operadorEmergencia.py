from src.businessLayer.businessEntities.persona import Persona

class OperadorEmergencia(Persona):
    disponibilidad: bool
    turno: str

    # Analizadores (Getters)
    def get_disponibilidad(self) -> bool:
        return self.disponibilidad
    
    def get_turno(self) -> str:
        return self.turno

    #modificadores (Setters)
    def set_disponibilidad(self, disponibilidad: bool) -> None:
        self.disponibilidad = disponibilidad

    def set_turno(self,turno: str) -> None:
        self.turno = turno

    #Método toString
    def __str__(self) -> str:
        return (f"OperadorEmergencia(id={self.id}, "
                f"disponibilidad={self.disponibilidad}, "
                f"turno={self.turno})")