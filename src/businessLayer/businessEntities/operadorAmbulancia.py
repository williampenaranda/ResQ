from src.businessLayer.businessEntities.persona import Persona

class OperadorAmbulancia(Persona):
    licencia: str
    
    def get_licencia(self) -> str:
        return self.licencia

    def set_licencia(self, licencia: str) -> None:
        self.licencia = licencia

    # Método toString
    def __str__(self) -> str:
        return (f"OperadorAmbulancia(id={self.id}, "
                f"licencia={self.licencia})")

