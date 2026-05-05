from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from datetime import date
from pydantic import EmailStr
from database import get_session
from models.miembros import Miembro
from models.entrenadores import Entrenador
from models.sedes import Sede
from schemas.miembros import CreateMiembro, UpdateMiembro, UpdateMiembroOptional

router = APIRouter(prefix="/miembro", tags=["Miembros"])

#Crear miembros
@router.post("/")
def create_miembro(data: CreateMiembro, session: Session = Depends(get_session)):
    if not data:
        raise HTTPException(status_code=400, detail="Debe suministrar todos los campos solicitados")
    existing = session.exec(
        select(Miembro).where(
            Miembro.ci == data.ci
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"El miembro con la cedula {data.ci} ya se encuentra registrado")
    sede = session.get(Sede, data.sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail=f"La sede con la ID {data.sede_id}")
    id_entrenador = session.exec(select(Entrenador).where(Entrenador.ci == data.entrenador_ci)).first()
    miembro = Miembro(
        ci = data.ci,
        nombre = data.nombre,
        apellido = data.apellido,
        fecha_nac = data.fecha_nac,
        telefono = data.telefono,
        email = data.email,
        fecha_inscripcion = data.fecha_inscripcion,
        estado = data.estado,
        entrenador_id = id_entrenador.id,
        sede_id = data.sede_id
    )
    session.add(miembro)
    session.commit()
    session.refresh(miembro)
    return {"message":f"Miembro {miembro.nombre} {miembro.apellido} creado de forma exitosa", "detail":miembro}

#Leer miembros (por ci, con filtro, etc)
@router.get("/all/", response_model=list[Miembro])
def get_all_miembro(session: Session = Depends(get_session)):
    miembro = session.exec(select(Miembro)).all()
    if not miembro:
        raise HTTPException(status_code=404, detail="No se ecuentran miembros registrados")
    return miembro

@router.get("/", response_model=list[Miembro])
def get_active_miembro(session: Session = Depends(get_session)):
    miembro = session.exec(
        select(Miembro).where(
            Miembro.estado == True
        )
    ).all()
    if not miembro:
        raise HTTPException(status_code=404, detail="No se encuentran miembros registrados o activos")
    return miembro

@router.get("/{ci}/")
def get_miembro_by_ci(miembro_ci: str, session: Session = Depends(get_session)):
    if not miembro_ci:
        raise HTTPException(status_code=400, detail="Debe proporcionar la cédula del miembro")
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail="No se encuentra un miembro asociado a la cédula ingresada")
    return miembro

@router.get("/{ci}/evaluaciones/")
def get_evaluaciones_miembro(miembro_ci: int, session: Session = Depends(get_session)):
    if not miembro_ci:
        raise HTTPException(status_code=400, detail="Debe proporcionar la cédula del miembro")
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"El miembro con la cédula {miembro_ci} no se encuentra registrado")
    if not miembro.estado:
        raise HTTPException(status_code=404, detail="El miembro seleccionado no se encuentra activo")
    evaluaciones = miembro.evaluaciones
    if not evaluaciones:
        raise HTTPException(status_code=404, detail=f"El miembro {miembro.nombre} {miembro.apellido} no tiene evaluaciones relacionadas")
    return {"message":f"Evaluaciones del miembro {miembro.nombre} {miembro.apellido}:", "detail":evaluaciones}

@router.get("/{ci}/planes/")
def get_planes_miembro(miembro_ci: int, session: Session = Depends(get_session)):
    if not miembro_ci:
        raise HTTPException(status_code=400, detail="Debe proporcionar la cédula del miembro")
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"El miembro con la cédula {miembro_ci} no se encuentra registrado")
    if not miembro.estado:
        raise HTTPException(status_code=404, detail="El miembro seleccionado no se encuentra activo")
    planes = miembro.planes
    if not planes:
        raise HTTPException(status_code=404, detail=f"El miembro {miembro.nombre} {miembro.apellido} no tiene planes relacionadas")
    return {"message":f"Planes del miembro {miembro.nombre} {miembro.apellido}:", "detail":planes}

@router.get("/{ci}/pagos/")
def get_pagos_miembro(miembro_ci: int, session: Session = Depends(get_session)):
    if not miembro_ci:
        raise HTTPException(status_code=400, detail="Debe proporcionar la cédula del miembro")
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"El miembro con la cédula {miembro_ci} no se encuentra registrado")
    if not miembro.estado:
        raise HTTPException(status_code=404, detail="El miembro seleccionado no se encuentra activo")
    pagos = miembro.pagos
    if not pagos:
        raise HTTPException(status_code=404, detail=f"El miembro {miembro.nombre} {miembro.apellido} no tiene pagos relacionadas")
    return {"message":f"Pagos del miembro {miembro.nombre} {miembro.apellido}:", "detail":pagos}

@router.get("/{ci}/entrenadores/")
def get_entrenadores_miembro(miembro_ci: int, session: Session = Depends(get_session)):
    if not miembro_ci:
        raise HTTPException(status_code=400, detail="Debe suministrar la cédula del miembro")
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No existe un miembro con la cédula {miembro_ci}")
    return miembro.entrenadores

@router.get("/filter/", response_model=list[Miembro])
def filter_miembro(
        miembro_ci: Optional[int] = Query(default=None), 
        miembro_nombre: Optional[str] = Query(default=None), 
        miembro_apellido: Optional[str] = Query(default=None), 
        miembro_email: Optional[EmailStr] = Query(default=None), 
        miembro_fecha_insc: Optional[date] = Query(default=None),
        entrenador_id: Optional[int] = Query(default=None),
        sede_id: Optional[int] = Query(default=None),
        plan_id: Optional[int] = Query(default=None),
        limite: int = Query(default=10),
        session: Session = Depends(get_session)
    ):
    if not miembro_ci and not miembro_nombre and not miembro_apellido and not miembro_email and not miembro_fecha_insc and not entrenador_id and not sede_id and not plan_id:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos uno de los campos para filtrar")
    query = select(Miembro).where(Miembro.estado==True)
    if miembro_ci:
        query = query.where(Miembro.ci == miembro_ci)
    if miembro_nombre:
        query = query.where(Miembro.nombre.ilike(f"%{miembro_nombre}%"))
    if miembro_apellido:
        query = query.where(Miembro.apellido.ilike(f"%{miembro_apellido}%"))
    if miembro_email:
        query = query.where(Miembro.email.ilike(f"%{miembro_email}%"))
    if miembro_fecha_insc:
        query = query.where(Miembro.fecha_insc.ilike(f"%{miembro_fecha_insc}%"))
    if entrenador_id:
        query = query.where(Miembro.entrenador_id.ilike(f"%{entrenador_id}%"))
    if sede_id:
        query = query.where(Miembro.sede_id.ilike(f"%{sede_id}%"))
    if plan_id:
        query = query.where(Miembro.plan_id.ilike(f"%{plan_id}%"))
    query.limit(limite)
    return session.exec(query).all()

#Actualiza miembros (patch y put)
@router.patch("/update/{ci}/")
def patch_miembro(miembro_ci: str, data: UpdateMiembroOptional, session: Session = Depends(get_session)):
    if not miembro_ci:
        raise HTTPException(status_code=400, detail="Debe proporcionar la cédula del miembro a actualizar")
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No se encuentra ningún miembro asociado a la cédula {miembro_ci}")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} se encuentra inactivo")
    nombre = miembro.nombre
    if data.ci:
        miembro.ci = data.ci
    if data.nombre:
        miembro.nombre = data.nombre
    if data.apellido:
        miembro.apellido = data.apellido
    if data.fecha_nac:
        miembro.fecha_nac = data.fecha_nac
    if data.telefono:
        miembro.telefono = data.telefono
    if data.email:
        miembro.email = data.email
    if data.entrenador_id:
        miembro.entrenador_id = data.entrenador_id
    if data.sede_id:
        miembro.sede_id = data.sede_id
    if data.plan_id:
        miembro.plan_id = data.plan_id
    session.commit()
    session.refresh(miembro)
    return {"message":f"El miembro {nombre} ha sido actualizado de forma exitosa", "detail":miembro}

@router.put("/update/{ci}/")
def put_miembro(miembro_ci: str, data: UpdateMiembro, session: Session = Depends(get_session)):
    if not miembro_ci:
        raise HTTPException(status_code=400, detail="Debe proporcionar la cédula del miembro a actualizar")
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No se encuentra ningún miembro asociado a la cédula {miembro_ci}")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} se encuentra inactivo")
    nombre = miembro.nombre
    miembro.ci = data.ci
    miembro.nombre = data.nombre
    miembro.apellido = data.apellido
    miembro.fecha_nac = data.fecha_nac
    miembro.telefono = data.telefono
    miembro.email = data.email
    miembro.entrenador_id = data.entrenador_id
    miembro.sede_id = data.sede_id
    miembro.plan_id = data.plan_id
    session.commit()
    session.refresh(miembro)
    return {"message":f"El miembro {nombre} ha sido actualizado de forma exitosa", "detail":miembro}

#Activar y desactivar (delete logico)
@router.delete("/{ci}/")
def inactivate_miembro(miembro_ci: str, session: Session = Depends(get_session)):
    if not miembro_ci:
        raise HTTPException(status_code=400, detail="Debe suministrar la cédula del miembro a inactivar")
    miembro = session.exec(select(Miembro).where(Miembro.ci == miembro_ci)).first()
    if not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} ya se encuentra inactivo")
    miembro.estado = False
    session.commit()
    return {"message":f"Miembro {miembro.nombre} inactivado de forma exitosa", "detail":miembro}

@router.patch("/{ci}/")
def activate_miembro(miembro_ci: str, session: Session = Depends(get_session)):
    if not miembro_ci:
        raise HTTPException(status_code=400, detail="Debe suministrar la cédula del miembro a activar")
    miembro = session.exec(select(Miembro).where(Miembro.ci == miembro_ci)).first()
    if miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} ya se encuentra activo")
    miembro.estado = True
    session.commit()
    return {"message":f"Miembro {miembro.nombre} activado de forma exitosa", "detail":miembro}