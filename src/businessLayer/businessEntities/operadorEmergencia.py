from src.businessLayer.businessEntities.persona import Persona

class OperadorEmergencia(Persona):
    disponibilidad: bool

    # Analizadores (Getters)
    def get_disponibilidad(self) -> bool:
        return self.disponibilidad

    #modificadores (Setters)
    def set_disponibilidad(self, disponibilidad: bool) -> None:
        self.disponibilidad = disponibilidad

    #Método toString
    def __str__(self) -> str:
        return (f"OperadorEmergencia(id={self.id}, "
                f"disponibilidad={self.disponibilidad})")