from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from typing import Optional
from datetime import date

class CreateMiembro(SQLModel):
    ci: int
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
    ci: int
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    fecha_nac: date
    telefono: str = Field(max_length=20)
    email: EmailStr = Field(max_length=255)
    entrenador_id: int 
    sede_id: int 
    plan_id: int 

class UpdateMiembroOptional(SQLModel):
    ci: Optional[int] = Field(default=None)
    nombre: Optional[str] = Field(default=None)
    apellido: Optional[str] = Field(default=None)
    fecha_nac: Optional[date] = Field(default=None)
    telefono: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    entrenador_id: Optional[int] = Field(default=None)
    sede_id: Optional[int] = Field(default=None)
    plan_id: Optional[int] = Field(default=None)