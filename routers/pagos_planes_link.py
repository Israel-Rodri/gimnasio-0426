from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models.pagos_planes_link import PagosPlanesLink
from models.pagos import Pago
from models.planes import Plan
from schemas.pagos_planes_link import CreatePagosPlanesLink

router = APIRouter(prefix="/pagos-planes", tags=["Enlace Pagos Planes"])

@router.post("/")
def link_pagos_planes(data: CreatePagosPlanesLink, session: Session = Depends(get_session)):
    if not data:
        raise HTTPException(status_code=400, detail="Debe proporcionar todos los datos solicitados")
    pago = session.get(Pago, data.pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail=f"No se encuentra una rutina asociada a la ID {data.pago_id}")
    plan = session.get(Plan, data.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No se encuentra un plan asociado a la ID {data.plan_id}")
    existing_link = session.exec(
        select(PagosPlanesLink).where(
            PagosPlanesLink.pago_id == data.pago_id,
            PagosPlanesLink.plan_id == data.plan_id
        )
    ).first()
    if existing_link:
        raise HTTPException(status_code=400, detail=f"Ya existe una relación entre la rutina {pago.nombre} y el plan {plan.nombre}")
    link = PagosPlanesLink(
        pago_id = data.pago_id,
        plan_id = data.plan_id
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    return {"message":f"Rutina {pago.nombre} asociada de forma exitosa al plan {plan.nombre}", "detail":link}