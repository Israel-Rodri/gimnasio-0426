from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date
from sqlalchemy.dialects.postgresql import JSONB

class CreateEvaluacionFisica(SQLModel):
    peso: float = Field(gt=0)
    talla: float = Field(gt=0)
    imc: Optional[float] = Field(default=None)
    estado_imc: Optional[str] = Field(default=None)
    medidas: Optional[dict] = Field(default=None, sa_type=JSONB)
    observaciones: Optional[str] = Field(default=None, max_length=200)
    fecha_evaluacion: date = Field(default_factory=date.today)
    miembro_ci: int

class UpdateEvaluacionFisica(SQLModel):
    peso: float = Field(gt=0)
    talla: float = Field(gt=0)
    imc: Optional[float] = Field(default=None, gt=0)
    estado_imc: Optional[str] = Field(default=None)
    medidas: dict
    observaciones: str = Field(max_length=200)
    fecha_evaluacion: date
    miembro_ci: int

class UpdateEvaluacionFisicaOptional(SQLModel):
    peso: Optional[float] = Field(default=None, gt=0)
    talla: Optional[float] = Field(default=None, gt=0)
    imc: Optional[float] = Field(default=None, gt=0)
    estado_imc: Optional[str] = Field(default=None)
    medidas: Optional[dict] = Field(default=None)
    observaciones: Optional[str] = Field(default=None, max_length=200)
    fecha_evaluacion: Optional[date] = Field(default=None)
    miembro_ci: Optional[int] = Field(default=None)