from sqlmodel import SQLModel, Field
from typing import Optional

class CreateRutina(SQLModel):
    nombre: str = Field(max_length=100)
    objetivo: Optional[str] = Field(default=None, max_length=200)
    nivel: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    duracion_estimada: Optional[float] = Field(default=None, gt=0)
    estado: bool = Field(default=True)
    plan_id: int 

class UpdateRutina(SQLModel):
    nombre: str = Field(max_length=100)
    objetivo: str = Field(max_length=200)
    nivel: str = Field(max_length=50)
    descripcion: str = Field(max_length=200)
    duracion_estimada: float = Field(gt=0)
    plan_id: int 

class UpdateRutinaOptional(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=100)
    objetivo: Optional[str] = Field(default=None, max_length=200)
    nivel: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    duracion_estimada: Optional[float] = Field(default=None, gt=0)
    plan_id: Optional[int] = Field(default=None)