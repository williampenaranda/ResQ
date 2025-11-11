import enum

class EstadoEmergencia(enum.Enum):
    CREADA = "CREADA"
    VALORADA = "VALORADA"
    ASIGNADA = "ASIGNADA"
    RESUELTA = "RESUELTA"
    CERRADA = "CERRADA"
    CANCELADA = "CANCELADA"