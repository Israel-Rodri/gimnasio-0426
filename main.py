from fastapi import FastAPI
from database import engine
from sqlmodel import SQLModel
from routers import sedes, metodos_pago, planes, entrenadores, miembros, evaluaciones, rutinas, pagos, miembros_entrenadores_link, pagos_planes_link, rutinas_planes_link

app = FastAPI()

app.include_router(sedes.router)
app.include_router(metodos_pago.router)
app.include_router(planes.router)
app.include_router(entrenadores.router)
app.include_router(miembros.router)
app.include_router(evaluaciones.router)
app.include_router(rutinas.router)
app.include_router(pagos.router)
app.include_router(miembros_entrenadores_link.router)
app.include_router(pagos_planes_link.router)
app.include_router(rutinas_planes_link.router)

@app.on_event("startup")
def init_db():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def root():
    return {"message":"Bienvenido al inicio!"}