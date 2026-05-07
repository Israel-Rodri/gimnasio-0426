# 📘 Documentación Técnica de los models del proyecto
> Generado automáticamente mediante script Bash

📅 Fecha: 2026-05-07 17:59:56
---

## Modelo de Entrenadores

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
---

## Modelo de Evaluaciones

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
---

## Modelo de Metodos de Pago

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
---

## Modelo Miembros Entrenadores Link

from sqlmodel import SQLModel, Field

class MiembrosEntrenadoresLink(SQLModel, table=True):
    __tablename__ = "miembros_entrenadores_link"
    miembro_id: int | None = Field(default=None, foreign_key="miembros.id", primary_key=True)
    entrenador_id: int | None = Field(default=None, foreign_key="entrenadores.id", primary_key=True)
---

## Modelo Miembros

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
---

## Modelo Pagos Planes Link

from sqlmodel import SQLModel, Field

class PagosPlanesLink(SQLModel, table=True):
    __tablename__ = "pagos_planes_link"
    pago_id: int | None = Field(default=None, foreign_key="pagos.id", primary_key=True)
    plan_id: int | None = Field(default=None, foreign_key="planes.id", primary_key=True)
---

## Modelo Pagos

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
---

## Modelo Planes

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
---

## Modelo Rutinas Planes Link

from sqlmodel import SQLModel, Field

class RutinasPlanesLink(SQLModel, table=True):
    __tablename__ = "rutinas_planes_link"
    rutina_id: int | None = Field(default=None, foreign_key="rutinas.id", primary_key=True)
    plan_id: int | None = Field(default=None, foreign_key="planes.id", primary_key=True)
---

## Modelo Rutinas

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
---

## Modelo Sedes

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, TYPE_CHECKING
from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
    from .entrenadores import Entrenador
    from .miembros import Miembro

class Sede(SQLModel, table=True):
    __tablename__ = "sedes"
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement":True})
    nombre: str = Field(max_length=50)
    direccion: str = Field(max_length=200)
    telefono: str = Field(max_length=20)
    horario: Optional[Dict] = Field(default=None, sa_type=JSONB)
    estado: bool = Field(default=True)
    #Relaciones
    miembros: list["Miembro"] = Relationship(back_populates="sede")
    entrenadores: list["Entrenador"] = Relationship(back_populates="sede")
---

🤖 *Documento generado automáticamente. Revisa los contenidos antes de compartir.*
📂 Repositorio: gimnasio-0426
