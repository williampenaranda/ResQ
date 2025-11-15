from src.businessLayer.businessEntities.persona import Persona

class OperadorAmbulancia(Persona):
    disponibilidad: bool
    licencia: str

    # Analizadores (Getters)
    def get_disponibilidad(self) -> bool:
        return self.disponibilidad
    
    def get_licencia(self) -> str:
        return self.licencia

    # Modificadores (Setters)
    def set_disponibilidad(self, disponibilidad: bool) -> None:
        self.disponibilidad = disponibilidad

    def set_licencia(self, licencia: str) -> None:
        self.licencia = licencia

    # Método toString
    def __str__(self) -> str:
        return (f"OperadorAmbulancia(id={self.id}, "
                f"disponibilidad={self.disponibilidad}, "
                f"licencia={self.licencia})")

