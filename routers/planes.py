from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from database import get_session
from models.planes import Plan
from models.miembros import Miembro
from schemas.planes import CreatePlan, UpdatePlan, UpdatePlanOptional

router = APIRouter(prefix=("/plan"), tags=["Planes de Ejercicio"])

#Crear planes
@router.post("/")
def create_plan(data: CreatePlan, session: Session = Depends(get_session)):
    if not data:
        raise HTTPException(status_code=400, detail="Debe ingresar todos los campos solicitados")
    existing = session.exec(
        select(Plan).where(
            Plan.nombre == data.nombre,
            Plan.precio == data.precio,
            Plan.beneficios == data.beneficios
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un plan con los datos ingresados")
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == data.miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"El miembro con la cédula {data.miembro_ci} no se encuetra registrado")
    plan = Plan(
        nombre = data.nombre,
        duracion = data.duracion,
        beneficios = data.beneficios,
        estado = data.estado,
        miembro_id = miembro.id 
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return {"message":f"Plan {plan.nombre} creado de forma exitosa", "detail":plan}

#Leer planes (por id, filtro, etc)
@router.get("/all/", response_model=list[Plan])
def get_all_plan(session: Session = Depends(get_session)):
    plan = session.exec(select(Plan)).all()
    if not plan:
        raise HTTPException(status_code=404, detail="No existe ningún plan de ejercicio registrado")
    return plan

@router.get("/", response_model=list[Plan])
def get_active_plan(session: Session = Depends(get_session)):
    plan = session.exec(select(Plan).where(Plan.estado==True)).all()
    if not plan:
        raise HTTPException(status_code=404, detail="No existe ningún plan de ejercicio o no hay ningún plan de ejercicio activo")
    return plan

@router.get("/{id}/")
def get_id_plan(plan_id: int, session: Session = Depends(get_session)):
    if not plan_id:
        raise HTTPException(status_code=400, detail="Debe suministrar la ID del plan")
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No se encuentra un plan asociado a la ID {plan_id}")
    if not plan.estado:
        raise HTTPException(status_code=400, detail=f"El plan {plan.nombre} se encuentra inactivo, activelo para acceder a su información")
    return {"message":f"Plan de entrenamiento {plan.nombre} encontrado de forma exitosa", "detail":plan}

@router.get("/filter/")
def filter_plan(
        nombre: Optional[str] = Query(default=None), 
        precio: Optional[float] = Query(default=None), 
        limite: int = 10,
        session: Session = Depends(get_session)
    ):
    if not nombre and not precio:
        raise HTTPException(status_code=400, detail="Debe suministrar al menos uno de los campos para filtrar")
    query = select(Plan).where(Plan.estado==True)
    if nombre:
        query = query.where(Plan.nombre.ilike(f"%{nombre}%"))
    if precio:
        query = query.where(Plan.precio.ilike(f"%{precio}%"))
    query = query.limit(limite)
    return session.exec(query).all()

@router.get("/{id}/pagos/")
def get_pagos_plan(plan_id: int, session: Session = Depends(get_session)):
    if not plan_id:
        raise HTTPException(status_code=400, detail="Debe suministrar la ID del plan")
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No existe un plan asociado a la ID {plan_id}")
    if not plan.estado:
        raise HTTPException(status_code=400, detail=f"El plan {plan.nombre} se encuentra inactivo, activelo para acceder a su información")
    pagos = plan.pagos
    if not pagos:
        raise HTTPException(status_code=404, detail=f"No existen pagos asociados al plan {plan.nombre}")
    return {"message":f"Pagos asociados al plan {plan.nombre}:", "detail":pagos}

@router.get("/{id}/rutinas/")
def get_rutinas_plan(plan_id: int, session: Session = Depends(get_session)):
    if not plan_id:
        raise HTTPException(status_code=400, detail="Debe suministrar la ID del plan")
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No existe un plan asociado a la ID {plan_id}")
    if not plan.estado:
        raise HTTPException(status_code=400, detail=f"El plan {plan.nombre} se encuentra inactivo, activelo para acceder a su información")
    rutinas = plan.rutinas
    if not rutinas:
        raise HTTPException(status_code=404, detail=f"No existen pagos asociados al plan {plan.nombre}")
    return {"message":f"Pagos asociados al plan {plan.nombre}:", "detail":rutinas}

#Actualizar planes (put y patch)
@router.put("/update/{id}/")
def put_plan(id: int, data: UpdatePlan, session: Session = Depends(get_session)):
    if not id:
        raise HTTPException(status_code=400, detail="Debe proporcionar la ID del plan de ejercicio a actualizar")
    plan = session.get(Plan, id)
    if not plan:
        raise HTTPException(status_code=404, detail="No existe nigún plan de ejercicio asociado a la ID proporcionada")
    if not plan.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar un plan de ejercicio inactivo")
    nombre = plan.nombre
    plan.nombre = data.nombre
    plan.duracion = data.duracion
    plan.precio = data.precio
    plan.beneficios = data.beneficios
    session.commit()
    session.refresh(plan)
    return {"message":f"El plan de ejercicio {nombre} ha sido actualizado de forma exitosa", "detail":plan}

@router.patch("/update/{id}/")
def patch_plan(id: int, data: UpdatePlanOptional, session: Session = Depends(get_session)):
    if not id:
        raise HTTPException(status_code=400, detail="Debe proporcionar la ID del plan a actiualizar")
    plan = session.get(Plan, id)
    if not plan:
        raise HTTPException(status_code=404, detail="No existe un plan asociado a la ID suministrada")
    if not plan.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar un plan inactivo")
    nombre = plan.nombre
    if data.nombre:
        plan.nombre = data.nombre
    if data.duracion:
        plan.duracion = data.duracion
    if data.precio:
        plan.precio = data.precio
    if data.beneficios:
        plan.beneficios = data.beneficios
    session.commit()
    session.refresh(plan)
    return {"message":f"El plan {nombre} fue actualizado de forma exitosa", "detail":plan}

#Activar y desactivar planes
@router.delete("/{id}/")
def inactivate_plan(id: int, session: Session = Depends(get_session)):
    if not id:
        raise HTTPException(status_code=400, detail="Debe suministrar la ID para inactivar un plan")
    plan = session.get(Plan, id)
    if not plan:
        raise HTTPException(status_code=404, detail="No existe un plan asociado a la ID suministrada")
    if not plan.estado:
        raise HTTPException(status_code=400, detail="El plan ya se encuentra inactivo")
    plan.estado = False
    session.commit()
    session.refresh(plan)
    return {"message":f"El plan {plan.nombre} fue inactivado exitosamente", "detail":plan}

@router.patch("/{id}/")
def activate_plan(id: int, session: Session = Depends(get_session)):
    if not id:
        raise HTTPException(status_code=400, detail="Debe suministrar la ID para inactivar un plan")
    plan = session.get(Plan, id)
    if not plan:
        raise HTTPException(status_code=404, detail="No existe un plan asociado a la ID suministrada")
    if plan.estado:
        raise HTTPException(status_code=400, detail="El plan ya se encuentra activo")
    plan.estado = True
    session.commit()
    session.refresh(plan)
    return {"message":f"El plan {plan.nombre} fue activado exitosamente", "detail":plan}