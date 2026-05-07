from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Column, ARRAY, String
from .pagos_planes_link import PagosPlanesLink
from .rutinas_planes_link import RutinasPlanesLink

if TYPE_CHECKING:
    from .miembros import Miembro
    from .pagos import Pago
    from .rutinas import Rutina

class Plan(SQLModel, table=True):
    __tablename__ = "planes"
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement":True})
    nombre: str = Field(max_length=50)
    duracion: float = Field(gt=0)
    precio: float = Field(gt=0)
    beneficios: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    estado: bool = Field(default=True)
    #Relaciones
    miembros: list["Miembro"] = Relationship(back_populates="planes")
    pagos: list["Pago"] = Relationship(back_populates="planes", link_model=PagosPlanesLink)
    rutinas: list["Rutina"] = Relationship(back_populates="planes", link_model=RutinasPlanesLink)