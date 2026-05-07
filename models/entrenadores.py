from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, ARRAY, String
from .miembros_entrenadores_link import MiembrosEntrenadoresLink

if TYPE_CHECKING:
    from .miembros import Miembro
    from .sedes import Sede
    from .evaluaciones import EvaluacionFisica

class Entrenador(SQLModel, table=True):
    __tablename__ = "entrenadores"
    id: int | None = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement":True})
    ci: str = Field(max_length=20)
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    especialidad: Optional[str] = Field(default=None, max_length=100)
    certificaciones: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = Field(default=None, max_length=255, unique=True, index=True)
    estado: bool = Field(default=True)
    #Llave foranea que conecta con sedes
    sede_id: int = Field(foreign_key="sedes.id", index=True)
    #relaciones
    sede: Optional["Sede"] = Relationship(back_populates="entrenadores")
    miembros: list["Miembro"] = Relationship(back_populates="entrenadores", link_model=MiembrosEntrenadoresLink)
    evaluaciones: list["EvaluacionFisica"] = Relationship(back_populates="entrenador")