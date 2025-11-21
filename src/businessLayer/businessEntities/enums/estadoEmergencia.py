import enum

class EstadoEmergencia(enum.Enum):
    CREADA = "CREADA"
    VALORADA = "VALORADA"
    ASIGNADA = "ASIGNADA"
    RESUELTA = "RESUELTA"
    CANCELADA = "CANCELADA"