from sqlmodel import SQLModel, Field
from typing import Optional, List
from pydantic import EmailStr

class CreateEntrenador(SQLModel):
    ci: int
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    especialidad: Optional[str] = Field(default=None, max_length=100)
    certificaciones: List[str] = Field(default_factory=list)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    estado: bool = Field(default=True)
    sede_id: int

class UpdateEntrenador(SQLModel):
    ci: int
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    especialidad: Optional[str] = Field(default=None, max_length=100)
    certificaciones: List[str] = Field(default_factory=list)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: EmailStr = Field(max_length=255)
    sede_id: int

class UpdateEntrenadorOptional(SQLModel):
    ci: Optional[int] = Field(default=None)
    nombre: Optional[str] = Field(default=None, max_length=50)
    apellido: Optional[str] = Field(default=None, max_length=50)
    especialidad: Optional[str] = Field(default=None, max_length=100)
    certificaciones: Optional[List[str]] = Field(default=None)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    sede_id: Optional[int] = Field(default=None)

class EntrenadorResponse(SQLModel):
    id: int
    ci: int
    nombre: str
    apellido: str
    especialidad: Optional[str] = None
    certificaciones: List[str] = []
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    sede_id: int
