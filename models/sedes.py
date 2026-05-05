from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
    from .entrenadores import Entrenador
    from .miembros import Miembro

class Sede(SQLModel, table=True):
    __tablename__ = "sedes"
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement":True})
    nombre: str = Field(max_length=50)
    direccion: str = Field(max_length=200)
    telefono: str = Field(max_length=20)
    horario: Optional[Dict] = Field(default=None, sa_type=JSONB)
    estado: bool = Field(default=True)
    #Relaciones
    miembros: list["Miembro"] = Relationship(back_populates="sede")
    entrenadores: list["Entrenador"] = Relationship(back_populates="sede")