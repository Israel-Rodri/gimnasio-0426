from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class CreateEvaluacionFisica(SQLModel):
    peso: float = Field(gt=0)
    talla: float = Field(gt=0)
    medidas: Optional[dict] = Field(default=None)
    observaciones: Optional[str] = Field(default=None, max_length=200)
    fecha_evaluacion: date = Field(default_factory=date.today)
    miembro_ci: int
    entrenador_ci: int

class UpdateEvaluacionFisica(SQLModel):
    peso: float = Field(gt=0)
    talla: float = Field(gt=0)
    medidas: Optional[dict] = Field(default=None)
    observaciones: Optional[str] = Field(default=None, max_length=200)
    fecha_evaluacion: date

class UpdateEvaluacionFisicaOptional(SQLModel):
    peso: Optional[float] = Field(default=None, gt=0)
    talla: Optional[float] = Field(default=None, gt=0)
    medidas: Optional[dict] = Field(default=None)
    observaciones: Optional[str] = Field(default=None, max_length=200)
    fecha_evaluacion: Optional[date] = Field(default=None)

class EvaluacionFisicaResponse(SQLModel):
    id: int
    peso: float
    talla: float
    imc: Optional[float] = None
    estado_imc: Optional[str] = None
    medidas: Optional[dict] = None
    observaciones: Optional[str] = None
    fecha_evaluacion: date
    miembro_id: int
    entrenador_id: int
