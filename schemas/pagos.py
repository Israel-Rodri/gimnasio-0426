from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class CreatePago(SQLModel):
    mensualidades: int = Field(gt=0)
    fecha: date
    monto: float = Field(gt=0)
    referencia: str = Field(max_length=100)
    estado: bool = Field(default=True)
    miembro_ci: int
    metodo_id: int

class UpdatePago(SQLModel):
    mensualidades: int = Field(gt=0)
    fecha: date
    monto: float = Field(gt=0)
    referencia: str = Field(max_length=100)
    miembro_ci: int
    metodo_id: int

class UpdatePagoOptional(SQLModel):
    mensualidades: Optional[int] = Field(gt=0)
    fecha: Optional[date]
    monto: Optional[float] = Field(gt=0)
    referencia: Optional[str] = Field(max_length=100)
    miembro_ci: Optional[int]
    metodo_id: Optional[int]