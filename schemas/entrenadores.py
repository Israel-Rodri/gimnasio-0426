from sqlmodel import SQLModel, Field
from typing import Optional, List
from pydantic import EmailStr
from sqlalchemy import Column, ARRAY, String

class CreateEntrenador(SQLModel):
    ci: int
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    especialidad: Optional[str] = Field(default=None, max_length=100)
    certificaciones: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = Field(default=None, max_length=255, unique=True, index=True)
    estado: bool = Field(default=True)
    sede_id: int

class UpdateEntrenador(SQLModel):
    ci: int
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    especialidad: str = Field(max_length=100)
    certificaciones: List[str]
    telefono: str = Field(max_length=20)
    email: EmailStr = Field(max_length=255)
    sede_id: int

class UpdateEntrenadorOptional(SQLModel):
    ci: Optional[int]
    nombre: Optional[str] = Field(max_length=50)
    apellido: Optional[str] = Field(max_length=50)
    especialidad: Optional[str] = Field(max_length=100)
    certificaciones: Optional[List[str]]
    telefono: Optional[str] = Field(max_length=20)
    email: Optional[EmailStr] = Field(max_length=255)
    sede_id: Optional[int]