from sqlmodel import SQLModel, Field
from typing import Optional, List

class CreatePlan(SQLModel):
    nombre: str = Field(max_length=50)
    duracion: float = Field(gt=0)
    precio: float = Field(gt=0)
    beneficios: List[str] = Field(default_factory=list)
    estado: bool = Field(default=True)
    miembro_id: int

class UpdatePlan(SQLModel):
    nombre: str = Field(max_length=50)
    duracion: float = Field(gt=0)
    precio: float = Field(gt=0)
    beneficios: List[str] = Field(default_factory=list)

class UpdatePlanOptional(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=50)
    duracion: Optional[float] = Field(default=None, gt=0)
    precio: Optional[float] = Field(default=None, gt=0)
    beneficios: Optional[List[str]] = Field(default=None)

class PlanResponse(SQLModel):
    id: int
    nombre: str
    duracion: float
    precio: float
    beneficios: List[str] = []
    miembro_id: int
