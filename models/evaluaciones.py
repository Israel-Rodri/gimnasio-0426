from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
    from .miembros import Miembro
    from .entrenadores import Entrenador

class EvaluacionFisica(SQLModel, table=True):
    __tablename__ = "evaluaciones_fisicas"
    id: int | None = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement":True})
    peso: float = Field(gt=0)
    talla: float = Field(gt=0)
    imc: Optional[float] = Field(default=None, gt=0)
    estado_imc: Optional[str] = Field(default=None)
    medidas: Optional[dict] = Field(default=None, sa_type=JSONB)
    observaciones: Optional[str] = Field(default=None, max_length=200)
    fecha_evaluacion: date = Field(default_factory=date.today)
    estado: bool = Field(default=True)
    #Foreign keys
    miembro_id: int = Field(foreign_key="miembros.id")
    entrenador_id: int = Field(foreign_key="entrenadores.id")
    #Relaciones
    miembro: Optional["Miembro"] = Relationship(back_populates="evaluaciones")
    entrenador: Optional["Entrenador"] = Relationship(back_populates="evaluaciones")