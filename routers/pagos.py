from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from datetime import date
from database import get_session
from models.pagos import Pago
from models.miembros import Miembro
from models.metodos_pago import MetodoPago
from models.planes import Plan
from schemas.pagos import CreatePago, UpdatePago, UpdatePagoOptional, PagoResponse
from schemas.planes import PlanResponse
from schemas.metodos_pago import MetodoPagoResponse
from schemas.base import MessageResponse

router = APIRouter(prefix="/pago", tags=["Pagos"])

@router.post("/", response_model=MessageResponse[PagoResponse])
def create_pago(data: CreatePago, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Pago).where(
            Pago.referencia == data.referencia
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Ya existe un pago con la referencia {data.referencia}")
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == data.miembro_ci
        )
    ).first()
    if not miembro or not miembro.estado:
        raise HTTPException(status_code=404, detail=f"El miembro con la cedula {data.miembro_ci} no se encuentra registrado o no se encuentra activo")
    metodo = session.get(MetodoPago, data.metodo_id)
    if not metodo or not metodo.estado:
        raise HTTPException(status_code=404, detail=f"El metodo de pago con la ID {data.metodo_id} no se encuentra registrado o no se encuentra activo")
    pago = Pago(
        mensualidades = data.mensualidades,
        fecha = data.fecha,
        monto = data.monto,
        referencia = data.referencia,
        estado = data.estado,
        miembro_id = miembro.id,
        metodo_id = data.metodo_id
    )
    session.add(pago)
    session.commit()
    session.refresh(pago)
    return {"message":f"Pago del cliente {miembro.nombre} con la referencia {pago.referencia} creado de forma exitosa", "detail":pago}

@router.get("/", response_model=list[PagoResponse])
def get_active_pagos(session: Session = Depends(get_session)):
    pagos = session.exec(
        select(Pago).where(
            Pago.estado == True
        )
    ).all()
    if not pagos:
        raise HTTPException(status_code=404, detail="No existen pagos registrados o activos")
    return pagos

@router.get("/all/", response_model=list[PagoResponse])
def get_all_pagos(session: Session = Depends(get_session)):
    pagos = session.exec(select(Pago)).all()
    if not pagos:
        raise HTTPException(status_code=404, detail="No se encuentran pagos registrados")
    return pagos

@router.get("/filter/", response_model=list[PagoResponse])
def filter_pago(
    pago_mensualidades: Optional[int] = Query(default=None),
    pago_fecha: Optional[date] = Query(default=None),
    pago_monto: Optional[float] = Query(default=None),
    pago_referencia: Optional[str] = Query(default=None),
    limite: int = 10,
    session: Session = Depends(get_session)
):
    if not pago_mensualidades and not pago_fecha and not pago_monto and not pago_referencia:
        raise HTTPException(status_code=400, detail="Debe suministrar al menos uno de los campos para filtrar")
    query = select(Pago).where(Pago.estado == True)
    if pago_mensualidades:
        query = query.where(Pago.mensualidades == pago_mensualidades)
    if pago_fecha:
        query = query.where(Pago.fecha == pago_fecha)
    if pago_monto:
        query = query.where(Pago.monto == pago_monto)
    if pago_referencia:
        query = query.where(Pago.referencia.ilike(f"%{pago_referencia}%"))
    query = query.limit(limite)
    return session.exec(query).all()

@router.get("/{pago_id}/", response_model=MessageResponse[PagoResponse])
def get_pago_by_id(pago_id: int, session: Session = Depends(get_session)):
    pago = session.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail=f"No se encuentra un pago registrado con la ID {pago_id}")
    return {"message": f"Pago con referencia {pago.referencia} encontrado de forma exitosa", "detail": pago}

@router.post("/{pago_id}/planes/{plan_id}/")
def asociar_plan_a_pago(pago_id: int, plan_id: int, session: Session = Depends(get_session)):
    pago = session.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail=f"No existe un pago asociado a la ID {pago_id}")
    if not pago.estado:
        raise HTTPException(status_code=400, detail=f"El pago con la referencia {pago.referencia} no se encuentra activo")
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No se encuentra un plan asociado a la ID {plan_id}")
    if plan in pago.planes:
        raise HTTPException(status_code=400, detail=f"Ya existe una relacion entre el pago con referencia {pago.referencia} y el plan {plan.nombre}")
    pago.planes.append(plan)
    session.commit()
    return {"message":f"Pago con referencia {pago.referencia} asociado de forma exitosa al plan {plan.nombre}"}

@router.get("/{pago_id}/planes/", response_model=MessageResponse[list[PlanResponse]])
def get_planes_pago(pago_id: int, session: Session = Depends(get_session)):
    pago = session.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail=f"No existe un pago asociado a la ID {pago_id}")
    if not pago.estado:
        raise HTTPException(status_code=400, detail=f"El pago con la referencia {pago.referencia} no se encuentra activo, activelo para poder acceder a sus datos")
    planes = pago.planes
    if not planes:
        raise HTTPException(status_code=404, detail=f"No existen planes asociados al pago con la referencia {pago.referencia}")
    return {"message":f"Planes asociados al pago con la referencia {pago.referencia}", "detail":planes}

@router.get("/{pago_id}/metodo/", response_model=MetodoPagoResponse)
def get_by_metodo(pago_id: int, session: Session = Depends(get_session)):
    pago = session.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail=f"No existe un pago asociado a la ID {pago_id}")
    metodo = pago.metodo_pago
    if not metodo:
        raise HTTPException(status_code=404, detail="No existen metodos de pago asociados al pago")
    return metodo

@router.delete("/{pago_id}/", response_model=MessageResponse[PagoResponse])
def inactivate_pago(pago_id: int, session: Session = Depends(get_session)):
    pago = session.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail=f"No existe un pago asociado a la ID {pago_id}")
    if not pago.estado:
        raise HTTPException(status_code=400, detail=f"El pago con referencia {pago.referencia} ya se encuentra inactivo")
    pago.estado = False
    session.commit()
    session.refresh(pago)
    return {"message":f"El pago con referencia {pago.referencia} fue inactivado de forma exitosa", "detail":pago}

@router.patch("/{pago_id}/", response_model=MessageResponse[PagoResponse])
def activate_pago(pago_id: int, session: Session = Depends(get_session)):
    pago = session.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail=f"No existe un pago asociado a la ID {pago_id}")
    if pago.estado:
        raise HTTPException(status_code=400, detail=f"El pago con referencia {pago.referencia} ya se encuentra activo")
    pago.estado = True
    session.commit()
    session.refresh(pago)
    return {"message":f"El pago con referencia {pago.referencia} fue activado de forma exitosa", "detail":pago}
