from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from typing import Optional
from datetime import date

class CreateMiembro(SQLModel):
    ci: str
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    fecha_nac: date
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    fecha_inscripcion: date = Field(default_factory=date.today)
    estado: bool = Field(default=True)
    entrenador_ci: Optional[int] = Field(default=None)
    sede_id: int

class UpdateMiembro(SQLModel):
    ci: str
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    fecha_nac: date
    telefono: str = Field(max_length=20)
    email: EmailStr = Field(max_length=255)
    entrenador_id: Optional[int] = Field(default=None)
    sede_id: int

class UpdateMiembroOptional(SQLModel):
    ci: Optional[str] = Field(default=None)
    nombre: Optional[str] = Field(default=None, max_length=50)
    apellido: Optional[str] = Field(default=None, max_length=50)
    fecha_nac: Optional[date] = Field(default=None)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    entrenador_id: Optional[int] = Field(default=None)
    sede_id: Optional[int] = Field(default=None)

class MiembroResponse(SQLModel):
    id: int
    ci: str
    nombre: str
    apellido: str
    fecha_nac: date
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    fecha_inscripcion: date
    entrenador_id: Optional[int] = None
    sede_id: int
