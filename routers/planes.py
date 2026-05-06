from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from database import get_session
from models.planes import Plan
from models.miembros import Miembro
from models.rutinas import Rutina
from schemas.planes import CreatePlan, UpdatePlan, UpdatePlanOptional, PlanResponse
from schemas.pagos import PagoResponse
from schemas.rutinas import RutinaResponse
from schemas.base import MessageResponse

router = APIRouter(prefix="/plan", tags=["Planes de Ejercicio"])

@router.post("/", response_model=MessageResponse[PlanResponse])
def create_plan(data: CreatePlan, session: Session = Depends(get_session)):
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
        raise HTTPException(status_code=404, detail=f"El miembro con la cedula {data.miembro_ci} no se encuentra registrado")
    plan = Plan(
        nombre = data.nombre,
        duracion = data.duracion,
        precio = data.precio,
        beneficios = data.beneficios,
        estado = data.estado,
        miembro_id = miembro.id
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return {"message":f"Plan {plan.nombre} creado de forma exitosa", "detail":plan}

@router.get("/all/", response_model=list[Plan])
def get_all_plan(session: Session = Depends(get_session)):
    plan = session.exec(select(Plan)).all()
    if not plan:
        raise HTTPException(status_code=404, detail="No existe ningun plan de ejercicio registrado")
    return plan

@router.get("/", response_model=list[PlanResponse])
def get_active_plan(session: Session = Depends(get_session)):
    plan = session.exec(select(Plan).where(Plan.estado==True)).all()
    if not plan:
        raise HTTPException(status_code=404, detail="No existe ningun plan de ejercicio o no hay ningun plan de ejercicio activo")
    return plan

@router.get("/filter/", response_model=list[PlanResponse])
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
        query = query.where(Plan.precio == precio)
    query = query.limit(limite)
    return session.exec(query).all()

@router.get("/{plan_id}/", response_model=MessageResponse[PlanResponse])
def get_id_plan(plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No se encuentra un plan asociado a la ID {plan_id}")
    if not plan.estado:
        raise HTTPException(status_code=400, detail=f"El plan {plan.nombre} se encuentra inactivo, activelo para acceder a su informacion")
    return {"message":f"Plan de entrenamiento {plan.nombre} encontrado de forma exitosa", "detail":plan}

@router.get("/{plan_id}/pagos/", response_model=MessageResponse[list[PagoResponse]])
def get_pagos_plan(plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No existe un plan asociado a la ID {plan_id}")
    if not plan.estado:
        raise HTTPException(status_code=400, detail=f"El plan {plan.nombre} se encuentra inactivo, activelo para acceder a su informacion")
    pagos = plan.pagos
    if not pagos:
        raise HTTPException(status_code=404, detail=f"No existen pagos asociados al plan {plan.nombre}")
    return {"message":f"Pagos asociados al plan {plan.nombre}:", "detail":pagos}

@router.post("/{plan_id}/rutinas/{rutina_id}/")
def asociar_rutina_a_plan(plan_id: int, rutina_id: int, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No existe un plan asociado a la ID {plan_id}")
    if not plan.estado:
        raise HTTPException(status_code=400, detail=f"El plan {plan.nombre} se encuentra inactivo")
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"No se encuentra una rutina asociada a la ID {rutina_id}")
    if rutina in plan.rutinas:
        raise HTTPException(status_code=400, detail=f"Ya existe una relacion entre la rutina {rutina.nombre} y el plan {plan.nombre}")
    plan.rutinas.append(rutina)
    session.commit()
    return {"message":f"Rutina {rutina.nombre} asociada de forma exitosa al plan {plan.nombre}"}

@router.get("/{plan_id}/rutinas/", response_model=MessageResponse[list[RutinaResponse]])
def get_rutinas_plan(plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No existe un plan asociado a la ID {plan_id}")
    if not plan.estado:
        raise HTTPException(status_code=400, detail=f"El plan {plan.nombre} se encuentra inactivo, activelo para acceder a su informacion")
    rutinas = plan.rutinas
    if not rutinas:
        raise HTTPException(status_code=404, detail=f"No existen rutinas asociadas al plan {plan.nombre}")
    return {"message":f"Rutinas asociadas al plan {plan.nombre}:", "detail":rutinas}

@router.put("/update/{plan_id}/", response_model=MessageResponse[PlanResponse])
def put_plan(plan_id: int, data: UpdatePlan, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No existe ningun plan de ejercicio asociado a la ID proporcionada")
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

@router.patch("/update/{plan_id}/", response_model=MessageResponse[PlanResponse])
def patch_plan(plan_id: int, data: UpdatePlanOptional, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No existe un plan asociado a la ID suministrada")
    if not plan.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar un plan inactivo")
    nombre = plan.nombre
    if data.nombre is not None:
        plan.nombre = data.nombre
    if data.duracion is not None:
        plan.duracion = data.duracion
    if data.precio is not None:
        plan.precio = data.precio
    if data.beneficios is not None:
        plan.beneficios = data.beneficios
    session.commit()
    session.refresh(plan)
    return {"message":f"El plan {nombre} fue actualizado de forma exitosa", "detail":plan}

@router.delete("/{plan_id}/", response_model=MessageResponse[PlanResponse])
def inactivate_plan(plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No existe un plan asociado a la ID suministrada")
    if not plan.estado:
        raise HTTPException(status_code=400, detail="El plan ya se encuentra inactivo")
    plan.estado = False
    session.commit()
    session.refresh(plan)
    return {"message":f"El plan {plan.nombre} fue inactivado exitosamente", "detail":plan}

@router.patch("/{plan_id}/", response_model=MessageResponse[PlanResponse])
def activate_plan(plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No existe un plan asociado a la ID suministrada")
    if plan.estado:
        raise HTTPException(status_code=400, detail="El plan ya se encuentra activo")
    plan.estado = True
    session.commit()
    session.refresh(plan)
    return {"message":f"El plan {plan.nombre} fue activado exitosamente", "detail":plan}
