from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from database import get_session
from models.sedes import Sede
from schemas.sedes import CreateSede, UpdateSede, UpdateSedeOptional

router = APIRouter(prefix="/sede", tags=["Sedes"])

@router.post("/")
def create_sede(data: CreateSede, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Sede).where(
            Sede.nombre == data.nombre
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una sede con el nombre ingresado")
    sede = Sede(
        nombre = data.nombre,
        direccion = data.direccion,
        telefono = data.telefono,
        horario = data.horario,
        estado = data.estado
    )
    session.add(sede)
    session.commit()
    session.refresh(sede)
    return {"message":f"Sede {sede.nombre} creada exitosamente", "detail":sede}

@router.get("/all/", response_model=list[Sede])
def get_all_sede(session: Session = Depends(get_session)):
    sede = session.exec(select(Sede)).all()
    if not sede:
        raise HTTPException(status_code=404, detail="No existen sedes registradas")
    return sede

@router.get("/", response_model=list[Sede])
def get_active_sede(session: Session = Depends(get_session)):
    sede = session.exec(select(Sede).where(Sede.estado==True)).all()
    if not sede:
        raise HTTPException(status_code=404, detail="No existen sedes activas")
    return sede

@router.get("/filter/", response_model=list[Sede])
def filter_sede(
        sede_nombre: Optional[str] = Query(None),
        sede_direccion: Optional[str] = Query(None),
        limite: int = 10,
        session: Session = Depends(get_session)
    ):
    if not sede_nombre and not sede_direccion:
        raise HTTPException(status_code=400, detail="Se debe llenar al menos uno de los campos para filtrar")
    query = select(Sede).where(Sede.estado == True)
    if sede_nombre:
        query = query.where(Sede.nombre.ilike(f"%{sede_nombre}%"))
    if sede_direccion:
        query = query.where(Sede.direccion.ilike(f"%{sede_direccion}%"))
    query = query.limit(limite)
    return session.exec(query).all()

@router.get("/{sede_id}/")
def get_id_sede(sede_id: int, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No se encuentra una sede asociada a la ID suministrada")
    if not sede.estado:
        raise HTTPException(status_code=400, detail=f"La sede {sede.nombre} se encuentra inactiva, activela para poder acceder a su informacion")
    return {"message":f"Sede {sede.nombre} encontrada de forma exitosa", "detail":sede}

@router.get("/{sede_id}/miembros/")
def get_miembros_sede(sede_id: int, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No se encuentra una sede asociada a la ID suministrada")
    if not sede.estado:
        raise HTTPException(status_code=400, detail=f"La sede {sede.nombre} se encuentra inactiva, activela para poder acceder a su informacion")
    miembros = sede.miembros
    if not miembros:
        raise HTTPException(status_code=404, detail=f"No existen miembros asociados a la sede con la ID {sede_id}")
    return {"message":f"Miembros de la sede con la ID {sede_id}", "detail":miembros}

@router.get("/{sede_id}/entrenadores/")
def get_entrenadores_sede(sede_id: int, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No se encuentra una sede asociada a la ID suministrada")
    if not sede.estado:
        raise HTTPException(status_code=400, detail=f"La sede {sede.nombre} se encuentra inactiva, activela para poder acceder a su informacion")
    entrenadores = sede.entrenadores
    if not entrenadores:
        raise HTTPException(status_code=404, detail=f"No existen entrenadores asociados a la sede con la ID {sede_id}")
    return {"message":f"Entrenadores de la sede con la ID {sede_id}", "detail":entrenadores}

@router.put("/update/{sede_id}/")
def put_sede(sede_id: int, data: UpdateSede, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No existe una sede con la id proporcionada")
    if not sede.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar una sede inactiva")
    sede.nombre = data.nombre
    sede.direccion = data.direccion
    sede.telefono = data.telefono
    sede.horario = data.horario
    session.commit()
    session.refresh(sede)
    return {"message":f"Sede {sede.nombre} actualizada de forma exitosa", "detail":sede}

@router.patch("/update/{sede_id}/")
def patch_sede(sede_id: int, data: UpdateSedeOptional, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No existe una sede asociada a la id suministrada")
    if not sede.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar una sede inactiva")
    if data.nombre is not None:
        sede.nombre = data.nombre
    if data.direccion is not None:
        sede.direccion = data.direccion
    if data.telefono is not None:
        sede.telefono = data.telefono
    if data.horario is not None:
        sede.horario = data.horario
    session.commit()
    session.refresh(sede)
    return {"message":f"Sede {sede.nombre} actualizada de forma correcta", "detail":sede}

@router.delete("/{sede_id}/")
def inactivate_sede(sede_id: int, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No existe una sede con la id suministrada")
    if not sede.estado:
        raise HTTPException(status_code=400, detail=f"La sede {sede.nombre} ya se encuentra inactiva")
    sede.estado = False
    session.commit()
    session.refresh(sede)
    return {"message":f"La sede {sede.nombre} fue inactivada de forma exitosa", "detail":sede}

@router.patch("/{sede_id}/")
def activate_sede(sede_id: int, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No existe una sede con la id suministrada")
    if sede.estado:
        raise HTTPException(status_code=400, detail=f"La sede {sede.nombre} ya se encuentra activa")
    sede.estado = True
    session.commit()
    session.refresh(sede)
    return {"message":f"La sede {sede.nombre} fue activada de forma exitosa", "detail":sede}
