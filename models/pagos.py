from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import date
from .pagos_planes_link import PagosPlanesLink

if TYPE_CHECKING:
    from .miembros import Miembro
    from .metodos_pago import MetodoPago
    from .planes import Plan

class Pago(SQLModel, table=True):
    __tablename__ = "pagos"
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement":True})
    mensualidades: int = Field(gt=0)
    fecha: date = Field(default_factory=date.today)
    monto: float = Field(gt=0)
    referencia: str = Field(max_length=100, unique=True, index=True)
    estado: bool = Field(default=True)
    #Foreign keys
    miembro_id: int = Field(foreign_key="miembros.id")
    metodo_id: int = Field(foreign_key="metodos_pago.id")
    #Relaciones
    miembro: Optional["Miembro"] = Relationship(back_populates="pagos")
    metodo_pago: Optional["MetodoPago"] = Relationship(back_populates="pagos")
    planes: list["Plan"] = Relationship(back_populates="pagos", link_model=PagosPlanesLink)