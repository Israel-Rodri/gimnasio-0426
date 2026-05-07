from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from typing import Optional, TYPE_CHECKING
from datetime import date
from .miembros_entrenadores_link import MiembrosEntrenadoresLink

if TYPE_CHECKING:
    from .sedes import Sede
    from .entrenadores import Entrenador
    from .planes import Plan
    from .evaluaciones import EvaluacionFisica
    from .pagos import Pago

class Miembro(SQLModel, table=True):
    __tablename__ = "miembros"
    id: int | None = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement":True})
    ci: str = Field(max_length=20)
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    fecha_nac: date
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = Field(default=None, max_length=255, unique=True, index=True)
    fecha_inscripcion: date = Field(default_factory=date.today)
    estado: bool = Field(default=True)
    entrenador_id: Optional[int] = Field(default=None, foreign_key="entrenadores.id", index=True)
    #Foreign keys
    sede_id: int = Field(foreign_key="sedes.id")
    plan_id: int = Field(foreign_key="planes.id")
    #Relaciones
    sede: Optional["Sede"] = Relationship(back_populates="miembros")
    planes: Optional["Plan"] = Relationship(back_populates="miembros")
    evaluaciones: list["EvaluacionFisica"] = Relationship(back_populates="miembro")
    pagos: list["Pago"] = Relationship(back_populates="miembro")
    entrenadores: list["Entrenador"] = Relationship(back_populates="miembros", link_model=MiembrosEntrenadoresLink)