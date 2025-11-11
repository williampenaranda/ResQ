from pydantic import BaseModel, Field
from datetime import date
from src.businessLayer.businessEntities.enums.tipoDocumento import TipoDocumento
from typing import Optional
    
class Persona(BaseModel):
    id: int
    nombre: str = Field(..., min_length=1)
    apellido: str = Field(..., min_length=1)
    fechaNacimiento: date
    tipoDocumento: TipoDocumento
    numeroDocumento: str = Field(..., min_length=1)
    nombre2: Optional[str] = None
    apellido2: Optional[str] = None

    # Analizadores (Getters)
    def get_id(self) -> int:
        """Retorna el ID de la persona."""
        return self.id
    
    def get_nombre(self) -> str:
        """Retorna el nombre de la persona."""
        return self.nombre
    
    def get_apellido(self) -> str:
        """Retorna el apellido de la persona."""
        return self.apellido
    
    def get_fecha_nacimiento(self) -> date:
        """Retorna la fecha de nacimiento de la persona."""
        return self.fechaNacimiento
    
    def get_documento(self) -> str:
        """Retorna el documento de la persona."""
        return self.documento
    
    def get_tipo_documento(self) -> TipoDocumento:
        """Retorna el tipo de documento de la persona."""
        return self.tipoDocumento
    
    def get_numero_documento(self) -> str:
        """Retorna el número de documento de la persona."""
        return self.numeroDocumento
    
    def get_nombre2(self) -> Optional[str]:
        """Retorna el segundo nombre de la persona (si existe)."""
        return self.nombre2
    
    def get_apellido2(self) -> Optional[str]:
        """Retorna el segundo apellido de la persona (si existe)."""
        return self.apellido2

    # Modificadores (Setters)
    def set_id(self, id: int) -> None:
        """Establece el ID de la persona."""
        self.id = id
    
    def set_nombre(self, nombre: str) -> None:
        """Establece el nombre de la persona."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre no puede estar vacío")
        self.nombre = nombre.strip()
    
    def set_apellido(self, apellido: str) -> None:
        """Establece el apellido de la persona."""
        if not apellido or not apellido.strip():
            raise ValueError("El apellido no puede estar vacío")
        self.apellido = apellido.strip()
    
    def set_fecha_nacimiento(self, fecha_nacimiento: date) -> None:
        """Establece la fecha de nacimiento de la persona."""
        self.fechaNacimiento = fecha_nacimiento
    
    def set_documento(self, documento: str) -> None:
        """Establece el documento de la persona."""
        if not documento or not documento.strip():
            raise ValueError("El documento no puede estar vacío")
        self.documento = documento.strip()
    
    def set_tipo_documento(self, tipo_documento: TipoDocumento) -> None:
        """Establece el tipo de documento de la persona."""
        self.tipoDocumento = tipo_documento
    
    def set_numero_documento(self, numero_documento: str) -> None:
        """Establece el número de documento de la persona."""
        if not numero_documento or not numero_documento.strip():
            raise ValueError("El número de documento no puede estar vacío")
        self.numeroDocumento = numero_documento.strip()
    
    def set_nombre2(self, nombre2: Optional[str]) -> None:
        """Establece el segundo nombre de la persona."""
        if nombre2 is not None:
            nombre2 = nombre2.strip()
            if not nombre2:
                nombre2 = None
        self.nombre2 = nombre2
    
    def set_apellido2(self, apellido2: Optional[str]) -> None:
        """Establece el segundo apellido de la persona."""
        if apellido2 is not None:
            apellido2 = apellido2.strip()
            if not apellido2:
                apellido2 = None
        self.apellido2 = apellido2

    # Método toString
    def __str__(self) -> str:
        """Retorna una representación en cadena de la persona."""
        nombre_completo = self.nombre
        if self.nombre2:
            nombre_completo += f" {self.nombre2}"
        nombre_completo += f" {self.apellido}"
        if self.apellido2:
            nombre_completo += f" {self.apellido2}"
        
        return (f"Persona(id={self.id}, nombre='{nombre_completo}', "
                f"fechaNacimiento={self.fechaNacimiento}, "
                f"tipoDocumento={self.tipoDocumento.value}, "
                f"numeroDocumento='{self.numeroDocumento}')")

