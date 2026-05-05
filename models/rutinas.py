from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from .rutinas_planes_link import RutinasPlanesLink

if TYPE_CHECKING:
    from .planes import Plan

class Rutina(SQLModel, table=True):
    __tablename__ = "rutinas"
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement":True})
    nombre: str = Field(max_length=100)
    objetivo: Optional[str] = Field(default=None, max_length=200)
    nivel: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    duracion_estimada: Optional[float] = Field(default=None, gt=0)
    estado: bool = Field(default=True)
    #Relaciones
    planes: list["Plan"] = Relationship(back_populates="rutinas", link_model=RutinasPlanesLink)