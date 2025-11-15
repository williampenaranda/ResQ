from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class Ubicacion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    latitud: float = Field(ge=-90.0, le=90.0)
    longitud: float = Field(ge=-180.0, le=180.0)
    fechaHora: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
