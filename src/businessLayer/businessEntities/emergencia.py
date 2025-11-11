from pydantic import BaseModel
from typing import Optional
from src.businessLayer.businessEntities.solicitud import Solicitud
from src.businessLayer.businessEntities.enums.estadoEmergencia import EstadoEmergencia
from src.businessLayer.businessEntities.enums.tipoAmbulancia import TipoAmbulancia
from src.businessLayer.businessEntities.enums.nivelPrioridad import NivelPrioridad
from src.businessLayer.businessEntities.persona import Persona

class Emergencia(BaseModel):
    id: Optional[int] = None
    solicitud: Solicitud
    estado: EstadoEmergencia
    tipoAmbulancia: TipoAmbulancia
    nivelPrioridad: NivelPrioridad
    descripcion: str
    id_operador: int
    paciente: Persona

    # Analizadores (Getters)
    def get_id(self) -> Optional[int]:
        """Retorna el ID de la emergencia."""
        return self.id
    
    def get_solicitud(self) -> Solicitud:
        """Retorna la solicitud de la emergencia."""
        return self.solicitud
    
    def get_estado(self) -> EstadoEmergencia:
        """Retorna el estado de la emergencia."""
        return self.estado
    
    def get_tipo_ambulancia(self) -> TipoAmbulancia:
        """Retorna el tipo de ambulancia asignada."""
        return self.tipoAmbulancia
    
    def get_nivel_prioridad(self) -> NivelPrioridad:
        """Retorna el nivel de prioridad de la emergencia."""
        return self.nivelPrioridad
    
    def get_descripcion(self) -> str:
        """Retorna la descripción de la emergencia."""
        return self.descripcion
    
    def get_id_operador(self) -> int:
        """Retorna el ID del operador asignado."""
        return self.id_operador
    
    def get_paciente(self) -> Persona:
        """Retorna el paciente de la emergencia."""
        return self.paciente

    # Modificadores (Setters)
    
    def set_solicitud(self, solicitud: Solicitud) -> None:
        """Establece la solicitud de la emergencia."""
        if solicitud is None:
            raise ValueError("La solicitud no puede ser None")
        if not isinstance(solicitud, Solicitud):
            raise TypeError("La solicitud debe ser una instancia de Solicitud")
        self.solicitud = solicitud
    
    def set_estado(self, estado: EstadoEmergencia) -> None:
        """Establece el estado de la emergencia."""
        if estado is None:
            raise ValueError("El estado no puede ser None")
        if not isinstance(estado, EstadoEmergencia):
            raise TypeError("El estado debe ser una instancia de EstadoEmergencia")
        self.estado = estado
    
    def set_tipo_ambulancia(self, tipo_ambulancia: TipoAmbulancia) -> None:
        """Establece el tipo de ambulancia asignada."""
        if tipo_ambulancia is None:
            raise ValueError("El tipo de ambulancia no puede ser None")
        if not isinstance(tipo_ambulancia, TipoAmbulancia):
            raise TypeError("El tipo de ambulancia debe ser una instancia de TipoAmbulancia")
        self.tipoAmbulancia = tipo_ambulancia
    
    def set_nivel_prioridad(self, nivel_prioridad: NivelPrioridad) -> None:
        """Establece el nivel de prioridad de la emergencia."""
        if nivel_prioridad is None:
            raise ValueError("El nivel de prioridad no puede ser None")
        if not isinstance(nivel_prioridad, NivelPrioridad):
            raise TypeError("El nivel de prioridad debe ser una instancia de NivelPrioridad")
        self.nivelPrioridad = nivel_prioridad
    
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
    
    def set_id_operador(self, id_operador: int) -> None:
        """Establece el ID del operador asignado."""
        if id_operador is None:
            raise ValueError("El ID del operador no puede ser None")
        if not isinstance(id_operador, int) or id_operador < 0:
            raise ValueError("El ID del operador debe ser un entero positivo")
        self.id_operador = id_operador
    
    def set_paciente(self, paciente: Persona) -> None:
        """Establece el paciente de la emergencia."""
        if paciente is None:
            raise ValueError("El paciente no puede ser None")
        if not isinstance(paciente, Persona):
            raise TypeError("El paciente debe ser una instancia de Persona")
        self.paciente = paciente

    # Método toString
    def __str__(self) -> str:
        """Retorna una representación en cadena de la emergencia."""
        descripcion_str = self.descripcion[:50] + "..." if len(self.descripcion) > 50 else self.descripcion
        return (f"Emergencia(id={self.id}, "
                f"estado={self.estado.value}, "
                f"tipoAmbulancia={self.tipoAmbulancia.value}, "
                f"nivelPrioridad={self.nivelPrioridad.value}, "
                f"descripcion='{descripcion_str}', "
                f"id_operador={self.id_operador}, "
                f"solicitud_id={self.solicitud.get_id()}, "
                f"paciente_id={self.paciente.get_id()})")
