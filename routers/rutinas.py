from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from database import get_session
from models.rutinas import Rutina
from schemas.rutinas import CreateRutina, UpdateRutina, UpdateRutinaOptional

router = APIRouter(prefix="/rutina", tags=["Rutinas de Ejercicio"])

@router.post("/")
def create_rutina(data: CreateRutina, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Rutina).where(
            Rutina.nombre == data.nombre
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Ya existe una rutina registrada con el nombre {data.nombre}")
    rutina = Rutina(
        nombre = data.nombre,
        objetivo = data.objetivo,
        nivel = data.nivel,
        descripcion = data.descripcion,
        duracion_estimada = data.duracion_estimada,
        estado = data.estado
    )
    session.add(rutina)
    session.commit()
    session.refresh(rutina)
    return {"message":f"Rutina {rutina.nombre} creada de forma exitosa", "detail":rutina}

@router.get("/all/", response_model=list[Rutina])
def get_all_rutina(session: Session = Depends(get_session)):
    rutina = session.exec(select(Rutina)).all()
    if not rutina:
        raise HTTPException(status_code=404, detail="No existen rutinas de ejercicio registradas")
    return rutina

@router.get("/", response_model=list[Rutina])
def get_active_rutina(session: Session = Depends(get_session)):
    rutina = session.exec(
        select(Rutina).where(
            Rutina.estado == True
        )
    ).all()
    if not rutina:
        raise HTTPException(status_code=404, detail="No existen rutinas registradas o no existen rutinas activas")
    return rutina

@router.get("/filter/")
def filter_rutina(
    rutina_nombre: Optional[str] = Query(default=None),
    rutina_objetivo: Optional[str] = Query(default=None),
    rutina_nivel: Optional[str] = Query(default=None),
    rutina_duracion: Optional[float] = Query(default=None),
    limite: int = 10,
    session: Session = Depends(get_session)
):
    if not rutina_nombre and not rutina_objetivo and not rutina_nivel and not rutina_duracion:
        raise HTTPException(status_code=400, detail="Es necesario suministrar al menos un campo para filtrar")
    query = select(Rutina).where(Rutina.estado == True)
    if rutina_nombre:
        query = query.where(Rutina.nombre.ilike(f"%{rutina_nombre}%"))
    if rutina_objetivo:
        query = query.where(Rutina.objetivo.ilike(f"%{rutina_objetivo}%"))
    if rutina_nivel:
        query = query.where(Rutina.nivel.ilike(f"%{rutina_nivel}%"))
    if rutina_duracion:
        query = query.where(Rutina.duracion_estimada == rutina_duracion)
    query = query.limit(limite)
    return session.exec(query).all()

@router.get("/{rutina_id}/")
def get_rutina_by_id(rutina_id: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"No existe una rutina asociada a la ID {rutina_id}")
    return rutina

@router.get("/{rutina_id}/planes/")
def get_planes_rutina(rutina_id: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"No existe una rutina asociada a la ID {rutina_id}")
    if not rutina.estado:
        raise HTTPException(status_code=400, detail=f"La rutina {rutina.nombre} no se encuentra activa, activela para acceder a su informacion")
    planes = rutina.planes
    if not planes:
        raise HTTPException(status_code=404, detail=f"La rutina {rutina.nombre} no tiene planes asociados")
    return {"message":f"Planes asociados a la rutina {rutina.nombre}:", "detail":planes}

@router.patch("/update/{rutina_id}/")
def patch_rutina(rutina_id: int, data: UpdateRutinaOptional, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail="No existe una rutina asociada a la ID suministrada")
    if not rutina.estado:
        raise HTTPException(status_code=400, detail=f"La rutina {rutina.nombre} se encuentra inactiva")
    nombre = rutina.nombre
    if data.nombre is not None:
        rutina.nombre = data.nombre
    if data.objetivo is not None:
        rutina.objetivo = data.objetivo
    if data.nivel is not None:
        rutina.nivel = data.nivel
    if data.descripcion is not None:
        rutina.descripcion = data.descripcion
    if data.duracion_estimada is not None:
        rutina.duracion_estimada = data.duracion_estimada
    session.commit()
    session.refresh(rutina)
    return {"message":f"La rutina {nombre} ha sido actualizada de forma exitosa", "detail":rutina}

@router.put("/update/{rutina_id}/")
def put_rutina(rutina_id: int, data: UpdateRutina, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail="No existe una rutina asociada a la ID suministrada")
    if not rutina.estado:
        raise HTTPException(status_code=400, detail=f"La rutina {rutina.nombre} se encuentra inactiva")
    nombre = rutina.nombre
    rutina.nombre = data.nombre
    rutina.objetivo = data.objetivo
    rutina.nivel = data.nivel
    rutina.descripcion = data.descripcion
    rutina.duracion_estimada = data.duracion_estimada
    session.commit()
    session.refresh(rutina)
    return {"message":f"La rutina {nombre} ha sido actualizada de forma exitosa", "detail":rutina}

@router.delete("/{rutina_id}/")
def inactivate_rutina(rutina_id: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail="No existe una rutina asociada a la ID suministrada")
    if not rutina.estado:
        raise HTTPException(status_code=400, detail=f"La rutina {rutina.nombre} ya se encuentra inactiva")
    rutina.estado = False
    session.commit()
    session.refresh(rutina)
    return {"message":f"La rutina {rutina.nombre} ha sido inactivada de forma exitosa", "detail":rutina}

@router.patch("/{rutina_id}/")
def activate_rutina(rutina_id: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail="No existe una rutina asociada a la ID suministrada")
    if rutina.estado:
        raise HTTPException(status_code=400, detail=f"La rutina {rutina.nombre} ya se encuentra activa")
    rutina.estado = True
    session.commit()
    session.refresh(rutina)
    return {"message":f"La rutina {rutina.nombre} ha sido activada de forma exitosa", "detail":rutina}
