from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class CreatePago(SQLModel):
    mensualidades: int = Field(gt=0)
    fecha: date = Field(default_factory=date.today)
    monto: float = Field(gt=0)
    referencia: str = Field(max_length=100)
    estado: bool = Field(default=True)
    miembro_id: int
    metodo_id: int

class UpdatePago(SQLModel):
    mensualidades: int = Field(gt=0)
    fecha: date
    monto: float = Field(gt=0)
    referencia: str = Field(max_length=100)
    metodo_id: int

class UpdatePagoOptional(SQLModel):
    mensualidades: Optional[int] = Field(default=None, gt=0)
    fecha: Optional[date] = Field(default=None)
    monto: Optional[float] = Field(default=None, gt=0)
    referencia: Optional[str] = Field(default=None, max_length=100)
    metodo_id: Optional[int] = Field(default=None)

class PagoResponse(SQLModel):
    id: int
    mensualidades: int
    fecha: date
    monto: float
    referencia: str
    miembro_id: int
    metodo_id: int
