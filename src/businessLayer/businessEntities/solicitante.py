from src.businessLayer.businessEntities.persona import Persona
from typing import Optional, List
from pydantic import field_validator, Field

class Solicitante(Persona):
    padecimientos: Optional[List[str]] = Field(default_factory=list)
    
    @field_validator("padecimientos", mode="before")
    def _validate_padecimientos(cls, v):
        if v is None:
            return []
        if not isinstance(v, list):
            return [v]
        return v

    # Analizadores (Getters)
    def get_padecimientos(self) -> List[str]:
        """Retorna la lista de padecimientos del solicitante."""
        return self.padecimientos if self.padecimientos else []

    # Modificadores (Setters)
    def set_padecimientos(self, padecimientos: Optional[List[str]]) -> None:
        """Establece la lista de padecimientos del solicitante."""
        if padecimientos is None:
            self.padecimientos = []
        elif isinstance(padecimientos, list):
            # Filtrar elementos vacíos y limpiar espacios
            self.padecimientos = [p.strip() for p in padecimientos if p and p.strip()]
        else:
            raise TypeError("padecimientos debe ser una lista o None")
    
    def agregar_padecimiento(self, padecimiento: str) -> None:
        """Agrega un padecimiento a la lista."""
        if not padecimiento or not padecimiento.strip():
            raise ValueError("El padecimiento no puede estar vacío")
        if self.padecimientos is None:
            self.padecimientos = []
        padecimiento_limpio = padecimiento.strip()
        if padecimiento_limpio not in self.padecimientos:
            self.padecimientos.append(padecimiento_limpio)
    
    def eliminar_padecimiento(self, padecimiento: str) -> None:
        """Elimina un padecimiento de la lista."""
        if self.padecimientos and padecimiento in self.padecimientos:
            self.padecimientos.remove(padecimiento)

    # Método toString
    def __str__(self) -> str:
        """Retorna una representación en cadena del solicitante."""
        nombre_completo = self.nombre
        if self.nombre2:
            nombre_completo += f" {self.nombre2}"
        nombre_completo += f" {self.apellido}"
        if self.apellido2:
            nombre_completo += f" {self.apellido2}"
        
        padecimientos_str = ", ".join(self.padecimientos) if self.padecimientos else "Ninguno"
        
        return (f"Solicitante(id={self.id}, nombre='{nombre_completo}', "
                f"fechaNacimiento={self.fechaNacimiento}, "
                f"tipoDocumento={self.tipoDocumento.value}, "
                f"numeroDocumento='{self.numeroDocumento}', "
                f"padecimientos=[{padecimientos_str}])")