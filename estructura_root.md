# 📘 Documentación Técnica de los models del proyecto
> Generado automáticamente mediante script Bash

📅 Fecha: 2026-05-07 18:11:04
---

## Modelo de Entrenadores

from sqlmodel import create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
---

## Modelo de Evaluaciones

from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine
from sqlmodel import SQLModel
from routers import sedes, metodos_pago, planes, entrenadores, miembros, evaluaciones, rutinas, pagos

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(sedes.router)
app.include_router(metodos_pago.router)
app.include_router(planes.router)
app.include_router(entrenadores.router)
app.include_router(miembros.router)
app.include_router(evaluaciones.router)
app.include_router(rutinas.router)
app.include_router(pagos.router)
@app.get("/")
def root():
    return {"message":"Bienvenido al inicio!"}

---

🤖 *Documento generado automáticamente. Revisa los contenidos antes de compartir.*
📂 Repositorio: gimnasio-0426
