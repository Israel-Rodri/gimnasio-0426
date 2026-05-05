from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from database import get_session
from models.metodos_pago import MetodoPago
from schemas.metodos_pago import CreateMetodoPago, UpdateMetodoPago, MetodoPagoResponse
from schemas.base import MessageResponse

router = APIRouter(prefix="/metodo-pago", tags=["Metodos de Pago"])

@router.post("/", response_model=MessageResponse[MetodoPagoResponse])
def create_metodo_pago(data: CreateMetodoPago, session: Session = Depends(get_session)):
    existing = session.exec(
        select(MetodoPago).where(
            MetodoPago.nombre == data.nombre
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un metodo de pago con ese nombre")
    metodo_pago = MetodoPago(**data.model_dump())
    session.add(metodo_pago)
    session.commit()
    session.refresh(metodo_pago)
    return {"message":f"El metodo de pago {metodo_pago.nombre} ha sido creado de forma exitosa", "detail":metodo_pago}

@router.get("/all/", response_model=list[MetodoPagoResponse])
def get_all_metodos_pago(session: Session = Depends(get_session)):
    metodo_pago = session.exec(select(MetodoPago)).all()
    if not metodo_pago:
        raise HTTPException(status_code=404, detail="No existe ningun metodo de pago registrado")
    return metodo_pago

@router.get("/", response_model=list[MetodoPagoResponse])
def get_active_metodo_pago(session: Session = Depends(get_session)):
    metodo_pago = session.exec(select(MetodoPago).where(MetodoPago.estado==True)).all()
    if not metodo_pago:
        raise HTTPException(status_code=404, detail="No existe ningun metodo de pago registrado o no hay ningun metodo de pago activo")
    return metodo_pago

@router.get("/filter/", response_model=MessageResponse[list[MetodoPagoResponse]])
def filter_metodo_pago(
    nombre: Optional[str] = Query(default=None),
    limite: int = Query(default=10),
    session: Session = Depends(get_session)
):
    if not nombre:
        raise HTTPException(status_code=400, detail="Debe proporcionar algun dato para filtrar")
    query = select(MetodoPago).where(MetodoPago.estado == True)
    query = query.where(MetodoPago.nombre.ilike(f"%{nombre}%"))
    query = query.limit(limite)
    metodo_pago = session.exec(query).all()
    if not metodo_pago:
        raise HTTPException(status_code=404, detail=f"No se encuentra un metodo de pago con el nombre '{nombre}'")
    return {"message":"Metodo de pago encontrado", "detail":metodo_pago}

@router.get("/{metodo_id}/", response_model=MessageResponse[MetodoPagoResponse])
def get_id_metodo_pago(metodo_id: int, session: Session = Depends(get_session)):
    metodo_pago = session.get(MetodoPago, metodo_id)
    if not metodo_pago:
        raise HTTPException(status_code=404, detail="No se encuentra un metodo de pago asociado a la ID suministrada")
    return {"message":f"Metodo de pago {metodo_pago.nombre} encontrado de forma exitosa", "detail":metodo_pago}

@router.put("/update/{metodo_id}/", response_model=MessageResponse[MetodoPagoResponse])
def put_metodos_pago(metodo_id: int, data: UpdateMetodoPago, session: Session = Depends(get_session)):
    metodo_pago = session.get(MetodoPago, metodo_id)
    if not metodo_pago:
        raise HTTPException(status_code=404, detail="No se encuentra un metodo de pago asociado a la ID suministrada")
    if not metodo_pago.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar un metodo de pago inactivo")
    nombre = metodo_pago.nombre
    metodo_pago.nombre = data.nombre
    session.commit()
    session.refresh(metodo_pago)
    return {"message":f"Metodo de pago {nombre} actualizado de forma correcta", "detail":metodo_pago}

@router.delete("/{metodo_id}/", response_model=MessageResponse[MetodoPagoResponse])
def inactivate_metodo_pago(metodo_id: int, session: Session = Depends(get_session)):
    metodo_pago = session.get(MetodoPago, metodo_id)
    if not metodo_pago:
        raise HTTPException(status_code=404, detail="No se encuentra ningun metodo de pago relacionado a la ID suministrada")
    if not metodo_pago.estado:
        raise HTTPException(status_code=400, detail=f"El metodo de pago {metodo_pago.nombre} ya se encuentra inactivo")
    metodo_pago.estado = False
    session.commit()
    session.refresh(metodo_pago)
    return {"message":f"El metodo de pago {metodo_pago.nombre} fue inactivado de forma exitosa", "detail":metodo_pago}

@router.patch("/{metodo_id}/", response_model=MessageResponse[MetodoPagoResponse])
def activate_metodo_pago(metodo_id: int, session: Session = Depends(get_session)):
    metodo_pago = session.get(MetodoPago, metodo_id)
    if not metodo_pago:
        raise HTTPException(status_code=404, detail="No se encuentra ningun metodo de pago relacionado a la ID suministrada")
    if metodo_pago.estado:
        raise HTTPException(status_code=400, detail=f"El metodo de pago {metodo_pago.nombre} ya se encuentra activo")
    metodo_pago.estado = True
    session.commit()
    session.refresh(metodo_pago)
    return {"message":f"Metodo de pago {metodo_pago.nombre} activado de forma exitosa", "detail":metodo_pago}
