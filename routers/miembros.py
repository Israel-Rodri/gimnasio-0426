from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from datetime import date
from pydantic import EmailStr
from database import get_session
from models.miembros import Miembro
from models.entrenadores import Entrenador
from models.sedes import Sede
from schemas.miembros import CreateMiembro, UpdateMiembro, UpdateMiembroOptional, MiembroResponse
from schemas.evaluaciones import EvaluacionFisicaResponse
from schemas.planes import PlanResponse
from schemas.pagos import PagoResponse
from schemas.entrenadores import EntrenadorResponse
from schemas.base import MessageResponse

router = APIRouter(prefix="/miembro", tags=["Miembros"])

@router.post("/", response_model=MessageResponse[MiembroResponse])
def create_miembro(data: CreateMiembro, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Miembro).where(
            Miembro.ci == data.ci
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"El miembro con la cedula {data.ci} ya se encuentra registrado")
    sede = session.get(Sede, data.sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail=f"La sede con la ID {data.sede_id} no se encuentra registrada")
    if data.entrenador_id is not None:
        entrenador = session.get(Entrenador, data.entrenador_id)
        if not entrenador:
            raise HTTPException(status_code=404, detail=f"No existe un entrenador con la ID {data.entrenador_id}")
    miembro = Miembro(
        ci = data.ci,
        nombre = data.nombre,
        apellido = data.apellido,
        fecha_nac = data.fecha_nac,
        telefono = data.telefono,
        email = data.email,
        fecha_inscripcion = data.fecha_inscripcion,
        estado = data.estado,
        entrenador_id = data.entrenador_id,
        sede_id = data.sede_id
    )
    session.add(miembro)
    session.commit()
    session.refresh(miembro)
    return {"message":f"Miembro {miembro.nombre} {miembro.apellido} creado de forma exitosa", "detail":miembro}

@router.get("/all/", response_model=list[Miembro])
def get_all_miembro(session: Session = Depends(get_session)):
    miembro = session.exec(select(Miembro)).all()
    if not miembro:
        raise HTTPException(status_code=404, detail="No se encuentran miembros registrados")
    return miembro

@router.get("/", response_model=list[MiembroResponse])
def get_active_miembro(session: Session = Depends(get_session)):
    miembro = session.exec(
        select(Miembro).where(
            Miembro.estado == True
        )
    ).all()
    if not miembro:
        raise HTTPException(status_code=404, detail="No se encuentran miembros registrados o activos")
    return miembro

@router.get("/filter/", response_model=list[MiembroResponse])
def filter_miembro(
        miembro_ci: Optional[str] = Query(default=None),
        miembro_nombre: Optional[str] = Query(default=None),
        miembro_apellido: Optional[str] = Query(default=None),
        miembro_email: Optional[EmailStr] = Query(default=None),
        miembro_fecha_insc: Optional[date] = Query(default=None),
        entrenador_id: Optional[int] = Query(default=None),
        sede_id: Optional[int] = Query(default=None),
        limite: int = Query(default=10),
        session: Session = Depends(get_session)
    ):
    if not miembro_ci and not miembro_nombre and not miembro_apellido and not miembro_email and not miembro_fecha_insc and not entrenador_id and not sede_id:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos uno de los campos para filtrar")
    query = select(Miembro).where(Miembro.estado==True)
    if miembro_ci:
        query = query.where(Miembro.ci.ilike(f"%{miembro_ci}%"))
    if miembro_nombre:
        query = query.where(Miembro.nombre.ilike(f"%{miembro_nombre}%"))
    if miembro_apellido:
        query = query.where(Miembro.apellido.ilike(f"%{miembro_apellido}%"))
    if miembro_email:
        query = query.where(Miembro.email.ilike(f"%{miembro_email}%"))
    if miembro_fecha_insc:
        query = query.where(Miembro.fecha_inscripcion == miembro_fecha_insc)
    if entrenador_id:
        query = query.where(Miembro.entrenador_id == entrenador_id)
    if sede_id:
        query = query.where(Miembro.sede_id == sede_id)
    query = query.limit(limite)
    return session.exec(query).all()

@router.get("/{miembro_id}/", response_model=MessageResponse[MiembroResponse])
def get_miembro_by_id(miembro_id: int, session: Session = Depends(get_session)):
    miembro = session.get(Miembro, miembro_id)
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No se encuentra un miembro asociado a la ID {miembro_id}")
    return {"message": f"Miembro {miembro.nombre} {miembro.apellido} encontrado de forma exitosa", "detail": miembro}

@router.get("/{miembro_id}/evaluaciones/", response_model=MessageResponse[list[EvaluacionFisicaResponse]])
def get_evaluaciones_miembro(miembro_id: int, session: Session = Depends(get_session)):
    miembro = session.get(Miembro, miembro_id)
    if not miembro:
        raise HTTPException(status_code=404, detail=f"El miembro con la ID {miembro_id} no se encuentra registrado")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail="El miembro seleccionado no se encuentra activo")
    evaluaciones = miembro.evaluaciones
    if not evaluaciones:
        raise HTTPException(status_code=404, detail=f"El miembro {miembro.nombre} {miembro.apellido} no tiene evaluaciones relacionadas")
    return {"message":f"Evaluaciones del miembro {miembro.nombre} {miembro.apellido}:", "detail":evaluaciones}

@router.get("/{miembro_id}/planes/", response_model=MessageResponse[list[PlanResponse]])
def get_planes_miembro(miembro_id: int, session: Session = Depends(get_session)):
    miembro = session.get(Miembro, miembro_id)
    if not miembro:
        raise HTTPException(status_code=404, detail=f"El miembro con la ID {miembro_id} no se encuentra registrado")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail="El miembro seleccionado no se encuentra activo")
    planes = miembro.planes
    if not planes:
        raise HTTPException(status_code=404, detail=f"El miembro {miembro.nombre} {miembro.apellido} no tiene planes relacionados")
    return {"message":f"Planes del miembro {miembro.nombre} {miembro.apellido}:", "detail":planes}

@router.get("/{miembro_id}/pagos/", response_model=MessageResponse[list[PagoResponse]])
def get_pagos_miembro(miembro_id: int, session: Session = Depends(get_session)):
    miembro = session.get(Miembro, miembro_id)
    if not miembro:
        raise HTTPException(status_code=404, detail=f"El miembro con la ID {miembro_id} no se encuentra registrado")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail="El miembro seleccionado no se encuentra activo")
    pagos = miembro.pagos
    if not pagos:
        raise HTTPException(status_code=404, detail=f"El miembro {miembro.nombre} {miembro.apellido} no tiene pagos relacionados")
    return {"message":f"Pagos del miembro {miembro.nombre} {miembro.apellido}:", "detail":pagos}

@router.post("/{miembro_id}/entrenadores/{entrenador_id}/")
def asociar_entrenador_a_miembro(miembro_id: int, entrenador_id: int, session: Session = Depends(get_session)):
    miembro = session.get(Miembro, miembro_id)
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No existe un miembro con la ID {miembro_id}")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} no se encuentra activo")
    entrenador = session.get(Entrenador, entrenador_id)
    if not entrenador:
        raise HTTPException(status_code=404, detail=f"No existe un entrenador con la ID {entrenador_id}")
    if entrenador in miembro.entrenadores:
        raise HTTPException(status_code=400, detail=f"Ya existe una relacion entre el miembro {miembro.nombre} y el entrenador {entrenador.nombre}")
    miembro.entrenadores.append(entrenador)
    session.commit()
    return {"message":f"Entrenador {entrenador.nombre} {entrenador.apellido} asociado de forma exitosa al miembro {miembro.nombre} {miembro.apellido}"}

@router.get("/{miembro_id}/entrenadores/", response_model=MessageResponse[list[EntrenadorResponse]])
def get_entrenadores_miembro(miembro_id: int, session: Session = Depends(get_session)):
    miembro = session.get(Miembro, miembro_id)
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No existe un miembro con la ID {miembro_id}")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} no se encuentra activo, activelo para acceder a su informacion")
    entrenadores = miembro.entrenadores
    if not entrenadores:
        raise HTTPException(status_code=404, detail=f"El miembro {miembro.nombre} {miembro.apellido} no tiene entrenadores asociados")
    return {"message":f"Entrenadores asociados al miembro {miembro.nombre} {miembro.apellido}:", "detail":entrenadores}

@router.patch("/update/{miembro_id}/", response_model=MessageResponse[MiembroResponse])
def patch_miembro(miembro_id: int, data: UpdateMiembroOptional, session: Session = Depends(get_session)):
    miembro = session.get(Miembro, miembro_id)
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No se encuentra ningun miembro asociado a la ID {miembro_id}")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} se encuentra inactivo")
    nombre = miembro.nombre
    if data.ci is not None:
        miembro.ci = data.ci
    if data.nombre is not None:
        miembro.nombre = data.nombre
    if data.apellido is not None:
        miembro.apellido = data.apellido
    if data.fecha_nac is not None:
        miembro.fecha_nac = data.fecha_nac
    if data.telefono is not None:
        miembro.telefono = data.telefono
    if data.email is not None:
        miembro.email = data.email
    if data.entrenador_id is not None:
        miembro.entrenador_id = data.entrenador_id
    if data.sede_id is not None:
        miembro.sede_id = data.sede_id
    session.commit()
    session.refresh(miembro)
    return {"message":f"El miembro {nombre} ha sido actualizado de forma exitosa", "detail":miembro}

@router.put("/update/{miembro_id}/", response_model=MessageResponse[MiembroResponse])
def put_miembro(miembro_id: int, data: UpdateMiembro, session: Session = Depends(get_session)):
    miembro = session.get(Miembro, miembro_id)
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No se encuentra ningun miembro asociado a la ID {miembro_id}")
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
    session.commit()
    session.refresh(miembro)
    return {"message":f"El miembro {nombre} ha sido actualizado de forma exitosa", "detail":miembro}

@router.delete("/{miembro_id}/", response_model=MessageResponse[MiembroResponse])
def inactivate_miembro(miembro_id: int, session: Session = Depends(get_session)):
    miembro = session.get(Miembro, miembro_id)
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No existe un miembro con la ID {miembro_id}")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} ya se encuentra inactivo")
    miembro.estado = False
    session.commit()
    session.refresh(miembro)
    return {"message":f"Miembro {miembro.nombre} inactivado de forma exitosa", "detail":miembro}

@router.patch("/{miembro_id}/", response_model=MessageResponse[MiembroResponse])
def activate_miembro(miembro_id: int, session: Session = Depends(get_session)):
    miembro = session.get(Miembro, miembro_id)
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No existe un miembro con la ID {miembro_id}")
    if miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} ya se encuentra activo")
    miembro.estado = True
    session.commit()
    session.refresh(miembro)
    return {"message":f"Miembro {miembro.nombre} activado de forma exitosa", "detail":miembro}
