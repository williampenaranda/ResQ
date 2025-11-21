import enum

class EstadoEmergencia(enum.Enum):
    CREADA = "CREADA"
    VALORADA = "VALORADA"
    ASIGNADA = "ASIGNADA"
    EN_ESCENA = "EN_ESCENA"
    RESUELTA = "RESUELTA"
    CANCELADA = "CANCELADA"