from sqlmodel import SQLModel, Field
from typing import Optional, List
from sqlalchemy import Column, ARRAY, String

class CreatePlan(SQLModel):
    nombre: str = Field(max_length=50)
    duracion: float = Field(gt=0)
    precio: float = Field(gt=0)
    beneficios: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    estado: bool = Field(default=True)
    miembro_ci: int

class UpdatePlan(SQLModel):
    nombre: str = Field(max_length=50)
    duracion: float = Field(gt=0)
    precio: float = Field(gt=0)
    beneficios: List[str]

class UpdatePlanOptional(SQLModel):
    nombre: Optional[str] = Field(max_length=50)
    duracion: Optional[float] = Field(gt=0)
    precio: Optional[float] = Field(gt=0)
    beneficios: Optional[List[str]]