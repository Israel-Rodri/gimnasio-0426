from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from datetime import date
from database import get_session
from models.pagos import Pago
from models.miembros import Miembro
from models.metodos_pago import MetodoPago
from schemas.pagos import CreatePago, UpdatePago, UpdatePagoOptional

router = APIRouter(prefix="/pago", tags=["Pagos"])

#Crear Pagos
@router.post("/")
def create_pago(data: CreatePago, session: Session = Depends(get_session)):
    if not data:
        raise HTTPException(status_code=400, detail="Debe suministrar todos los datos solicitados")
    exisiting = session.exec(
        select(Pago).where(
            Pago.referencia == data.referencia,
            Pago.fecha == data.fecha,
            Pago.monto == data.monto
        )
    ).first()
    if exisiting:
        raise HTTPException(status_code=400, detail=f"Ya existe un pago con la referencia {data.referencia} por el monto {data.monto} realizado el día {data.fecha}")
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == data.miembro_ci
        )
    ).first()
    if not miembro or not miembro.estado:
        raise HTTPException(status_code=404, detail=f"El miembro con la cédula {data.miembro_ci} no se encuentra registrado o no se encuentra activo")
    metodo = session.get(MetodoPago, data.metodo_id)
    if not metodo or not metodo.estado:
        raise HTTPException(status_code=404, detail=f"El método de pago con la ID {data.metodo_id} no se encuentra registrado o no se encuentra activo")
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

#Leer pagos (por id, filtro, etc.)
@router.get("/", response_model=list[Pago])
def get_active_pagos(session: Session = Depends(get_session)):
    pagos = session.exec(
        select(Pago).where(
            Pago.estado == True
        )
    ).all()
    if not pagos:
        raise HTTPException(status_code=404, detail="No existen pagos registrados o activos")
    return pagos

@router.get("/all/", response_model=list[Pago])
def get_all_pagos(session: Session = Depends(get_session)):
    pagos = session.exec(
        select(Pago)
    ).all()
    if not pagos:
        raise HTTPException(status_code=404, detail="No se encuentran pagos registrados")
    return pagos

@router.get("/{pago_id}/")
def get_pago_by_id(pago_id: int, session: Session = Depends(get_session)):
    if not pago_id:
        raise HTTPException(status_code=400, detail="Debe suministrar la ID del pago")
    pago = session.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail=f"No se encuentra un pago registrado con la ID {pago_id}")
    return pago

@router.get("/{pago_id}/planes/")
def get_planes_pago(pago_id: int, session: Session = Depends(get_session)):
    if not pago_id:
        raise HTTPException(status_code=400, detail="Debe suministrar la ID del pago")
    pago = session.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail=f"No existe un pago asociado a la ID {pago_id}")
    if not pago.estado:
        raise HTTPException(status_code=400, detail=f"El pago con la referencia {pago.referencia} no se encuentra activo, activelo para poder acceder a sus datos")
    planes = pago.planes
    if planes:
        raise HTTPException(status_code=404, detail=f"No existen planes asociados al pago con la referencia {pago.referencia}")
    return {"message":f"Rutinas asociadas al pago con la referencia {pago.referencia}", "detail":planes}

@router.get("/filter/")
def filter_pago(
    pago_mensualidades: Optional[int] = Query(default=None),
    pago_fecha: Optional[date] = Query(default=None),
    pago_monto: Optional[float] = Query(default=None),
    pago_referencia: Optional[str] = Query(default=None),
    limite: int = 10,
    session: Session = Depends(get_session)
):
    if not pago_mensualidades or not pago_fecha or not pago_monto or not pago_referencia:
        raise HTTPException(status_code=400, detail="Debe suministrar al menos uno de los campos para filtrar")
    query = select(Pago).where(Pago.estado == True)
    if pago_mensualidades:
        query = query.where(Pago.mensualidades.ilike(f"%{pago_mensualidades}%"))
    if pago_fecha:
        query = query.where(Pago.fecha.ilike(f"%{pago_fecha}%"))
    if pago_monto:
        query = query.where(Pago.monto.ilike(f"%{pago_monto}%"))
    if pago_referencia:
        query = query.where(Pago.referencia.ilike(f"%{pago_referencia}%"))
    query.limit(limite)
    return session.exec(query).all()

@router.get("/{pago_id}/metodo/")
def get_by_metodo(pago_id: int, session: Session = Depends(get_session)):
    pago = session.get(Pago, pago_id)
    metodo = pago.metodo_pago
    if not metodo:
        raise HTTPException(status_code=404, detail="No existen metodos de pago asociados al pago")
    return metodo