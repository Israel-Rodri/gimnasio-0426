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
