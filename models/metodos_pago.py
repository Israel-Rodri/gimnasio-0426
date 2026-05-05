from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .pagos import Pago

class MetodoPago(SQLModel, table=True):
    __tablename__ = "metodos_pago"
    id: int | None = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement":True})
    nombre: str = Field(max_length=50, unique=True, index=True)
    estado: bool = Field(default=True)
    #Relaciones
    pagos: list["Pago"] = Relationship(back_populates="metodo_pago")