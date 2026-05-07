# 📘 Documentación Técnica de los models del proyecto
> Generado automáticamente mediante script Bash

📅 Fecha: 2026-05-07 18:01:16
---

## Modelo de Entrenadores

from sqlmodel import SQLModel, Field
from typing import Optional, List
from pydantic import EmailStr

class CreateEntrenador(SQLModel):
    ci: str
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    especialidad: Optional[str] = Field(default=None, max_length=100)
    certificaciones: List[str] = Field(default_factory=list)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    estado: bool = Field(default=True)
    sede_id: int

class UpdateEntrenador(SQLModel):
    ci: str
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    especialidad: Optional[str] = Field(default=None, max_length=100)
    certificaciones: List[str] = Field(default_factory=list)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: EmailStr = Field(max_length=255)
    sede_id: int

class UpdateEntrenadorOptional(SQLModel):
    ci: Optional[str] = Field(default=None)
    nombre: Optional[str] = Field(default=None, max_length=50)
    apellido: Optional[str] = Field(default=None, max_length=50)
    especialidad: Optional[str] = Field(default=None, max_length=100)
    certificaciones: Optional[List[str]] = Field(default=None)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    sede_id: Optional[int] = Field(default=None)

class EntrenadorResponse(SQLModel):
    id: int
    ci: str
    nombre: str
    apellido: str
    especialidad: Optional[str] = None
    certificaciones: List[str] = []
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    sede_id: int

---

## Modelo de Evaluaciones

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class CreateEvaluacionFisica(SQLModel):
    peso: float = Field(gt=0)
    talla: float = Field(gt=0)
    medidas: Optional[dict] = Field(default=None)
    observaciones: Optional[str] = Field(default=None, max_length=200)
    fecha_evaluacion: date = Field(default_factory=date.today)
    miembro_id: int
    entrenador_id: int

class UpdateEvaluacionFisica(SQLModel):
    peso: float = Field(gt=0)
    talla: float = Field(gt=0)
    medidas: Optional[dict] = Field(default=None)
    observaciones: Optional[str] = Field(default=None, max_length=200)
    fecha_evaluacion: date

class UpdateEvaluacionFisicaOptional(SQLModel):
    peso: Optional[float] = Field(default=None, gt=0)
    talla: Optional[float] = Field(default=None, gt=0)
    medidas: Optional[dict] = Field(default=None)
    observaciones: Optional[str] = Field(default=None, max_length=200)
    fecha_evaluacion: Optional[date] = Field(default=None)

class EvaluacionFisicaResponse(SQLModel):
    id: int
    peso: float
    talla: float
    imc: Optional[float] = None
    estado_imc: Optional[str] = None
    medidas: Optional[dict] = None
    observaciones: Optional[str] = None
    fecha_evaluacion: date
    miembro_id: int
    entrenador_id: int

---

## Modelo de Metodos de Pago

from sqlmodel import SQLModel, Field

class CreateMetodoPago(SQLModel):
    nombre: str = Field(max_length=50)
    estado: bool = Field(default=True)

class UpdateMetodoPago(SQLModel):
    nombre: str = Field(max_length=50)

class MetodoPagoResponse(SQLModel):
    id: int
    nombre: str
---

## Modelo Miembros Entrenadores Link

from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from typing import Optional
from datetime import date

class CreateMiembro(SQLModel):
    ci: str
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    fecha_nac: date
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    fecha_inscripcion: date = Field(default_factory=date.today)
    estado: bool = Field(default=True)
    entrenador_id: Optional[int] = Field(default=None)
    sede_id: int

class UpdateMiembro(SQLModel):
    ci: str
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    fecha_nac: date
    telefono: str = Field(max_length=20)
    email: EmailStr = Field(max_length=255)
    entrenador_id: Optional[int] = Field(default=None)
    sede_id: int

class UpdateMiembroOptional(SQLModel):
    ci: Optional[str] = Field(default=None)
    nombre: Optional[str] = Field(default=None, max_length=50)
    apellido: Optional[str] = Field(default=None, max_length=50)
    fecha_nac: Optional[date] = Field(default=None)
    telefono: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    entrenador_id: Optional[int] = Field(default=None)
    sede_id: Optional[int] = Field(default=None)

class MiembroResponse(SQLModel):
    id: int
    ci: str
    nombre: str
    apellido: str
    fecha_nac: date
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    fecha_inscripcion: date
    entrenador_id: Optional[int] = None
    sede_id: int

---

## Modelo Miembros

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

---

## Modelo Pagos Planes Link

from sqlmodel import SQLModel, Field
from typing import Optional, List

class CreatePlan(SQLModel):
    nombre: str = Field(max_length=50)
    duracion: float = Field(gt=0)
    precio: float = Field(gt=0)
    beneficios: List[str] = Field(default_factory=list)
    estado: bool = Field(default=True)
    miembro_id: int

class UpdatePlan(SQLModel):
    nombre: str = Field(max_length=50)
    duracion: float = Field(gt=0)
    precio: float = Field(gt=0)
    beneficios: List[str] = Field(default_factory=list)

class UpdatePlanOptional(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=50)
    duracion: Optional[float] = Field(default=None, gt=0)
    precio: Optional[float] = Field(default=None, gt=0)
    beneficios: Optional[List[str]] = Field(default=None)

class PlanResponse(SQLModel):
    id: int
    nombre: str
    duracion: float
    precio: float
    beneficios: List[str] = []
    miembro_id: int

---

## Modelo Pagos

from sqlmodel import SQLModel, Field
from typing import Optional

class CreateRutina(SQLModel):
    nombre: str = Field(max_length=100)
    objetivo: Optional[str] = Field(default=None, max_length=200)
    nivel: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    duracion_estimada: Optional[float] = Field(default=None, gt=0)
    estado: bool = Field(default=True)

class UpdateRutina(SQLModel):
    nombre: str = Field(max_length=100)
    objetivo: Optional[str] = Field(default=None, max_length=200)
    nivel: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    duracion_estimada: Optional[float] = Field(default=None, gt=0)

class UpdateRutinaOptional(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=100)
    objetivo: Optional[str] = Field(default=None, max_length=200)
    nivel: Optional[str] = Field(default=None, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    duracion_estimada: Optional[float] = Field(default=None, gt=0)

class RutinaResponse(SQLModel):
    id: int
    nombre: str
    objetivo: Optional[str] = None
    nivel: Optional[str] = None
    descripcion: Optional[str] = None
    duracion_estimada: Optional[float] = None

---

## Modelo Planes

from sqlmodel import SQLModel, Field
from typing import Optional, Dict

class CreateSede(SQLModel):
    nombre: str = Field(max_length=50)
    direccion: str = Field(max_length=200)
    telefono: str = Field(max_length=20)
    horario: Optional[Dict] = Field(default=None)
    estado: bool = Field(default=True)

class UpdateSede(SQLModel):
    nombre: str = Field(max_length=50)
    direccion: str = Field(max_length=200)
    telefono: str = Field(max_length=20)
    horario: Optional[Dict] = Field(default=None)

class UpdateSedeOptional(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=50)
    direccion: Optional[str] = Field(default=None, max_length=200)
    telefono: Optional[str] = Field(default=None, max_length=20)
    horario: Optional[Dict] = Field(default=None)

class SedeResponse(SQLModel):
    id: int
    nombre: str
    direccion: str
    telefono: str
    horario: Optional[Dict] = None

---

🤖 *Documento generado automáticamente. Revisa los contenidos antes de compartir.*
📂 Repositorio: gimnasio-0426
