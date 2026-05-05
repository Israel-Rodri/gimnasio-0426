from sqlmodel import SQLModel, Field
from typing import Optional, Dict
from sqlalchemy.dialects.postgresql import JSONB

class CreateSede(SQLModel):
    nombre: str = Field(max_length=50)
    direccion: str = Field(max_length=200)
    telefono: str = Field(max_length=20)
    horario: Optional[Dict] = Field(default=None, sa_type=JSONB)
    estado: bool = Field(default=True)

class UpdateSede(SQLModel):
    nombre: str = Field(max_length=50)
    direccion: str = Field(max_length=200)
    telefono: str = Field(max_length=20)
    horario: Dict

class UpdateSedeOptional(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=50)
    direccion: Optional[str] = Field(default=None, max_length=200)
    telefono: Optional[str] = Field(default=None, max_length=20)
    horario: Optional[Dict] = Field(default=None)