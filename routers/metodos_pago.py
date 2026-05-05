from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models.metodos_pago import MetodoPago
from schemas.metodos_pago import CreateMetodoPago, UpdateMetodoPago

router = APIRouter(prefix="/metodo-pago", tags=["Metodos de Pago"])

@router.post("/")
def create_metodo_pago(data: CreateMetodoPago, session: Session = Depends(get_session)):
    if not data:
        raise HTTPException(status_code=400, detail="De rellenar todos los campos")
    existing = session.exec(
        select(MetodoPago).where(
            MetodoPago.nombre == data.nombre
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un método de pago con ese nombre")
    metodo_pago = MetodoPago(**data.model_dump())
    session.add(metodo_pago)
    session.commit()
    session.refresh(metodo_pago)
    return {"message":f"El metodo de pago {metodo_pago.nombre} ha sido creado de forma exitosa", "detail":metodo_pago}

@router.get("/all/", response_model=list[MetodoPago])
def get_all_metodos_pago(session: Session = Depends(get_session)):
    metodo_pago = session.exec(select(MetodoPago)).all()
    if not metodo_pago:
        raise HTTPException(status_code=404, detail="No existe ningún método de pago registrado")
    return metodo_pago

@router.get("/", response_model=list[MetodoPago])
def get_active_metodo_pago(session: Session = Depends(get_session)):
    metodo_pago = session.exec(select(MetodoPago).where(MetodoPago.estado==True)).all()
    if not metodo_pago:
        raise HTTPException(status_code=404, detail="No existe ningún método de pago registrado o no hay ningún método de pago activo")
    return metodo_pago

@router.get("/{id}/")
def get_if_metodo_pago(id: int, session: Session = Depends(get_session)):
    if not id:
        raise HTTPException(status_code=400, detail="Debe suministrar la ID del método de pago")
    metodo_pago = session.get(MetodoPago, id)
    if not metodo_pago:
        raise HTTPException(status_code=404, detail="No se encuentra un método de pago aosicado a la ID suministrada")
    return {"message":f"Método de pago {metodo_pago.nombre} encontrado de forma exitosa", "detail":metodo_pago}

@router.get("/filter/")
def filter_metodo_pago(nombre: str, session: Session = Depends(get_session)):
    if not nombre:
        raise HTTPException(status_code=400, detail="Debe proporcionar algún dato para filtrar")
    metodo_pago = session.exec(
        select(MetodoPago).where(
            MetodoPago.nombre == nombre
        )
    ).all()
    if not metodo_pago:
        raise HTTPException(status_code=404, detail=f"No se encuentra un método de pago con el nombre '{nombre}'")
    return {"message":f"Método de pago encontrado", "detail":metodo_pago}

@router.put("/update/{id}/")
def put_metodos_pago(id: int, data: UpdateMetodoPago, session: Session = Depends(get_session)):
    if not id:
        raise HTTPException(status_code=400, detail="Debe proporcionar la ID del metodo de pago")
    metodo_pago = session.get(MetodoPago, id)
    if not metodo_pago:
        raise HTTPException(status_code=404, detail="No se encutra un método de pago asociado a la ID suministrada")
    if not metodo_pago.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar un método de pago inactivo")
    nombre = metodo_pago.nombre
    metodo_pago.nombre = data.nombre
    session.commit()
    session.refresh(metodo_pago)
    return {"message":f"Método de pago {nombre} actualizado de forma correcta", "detail":metodo_pago}

@router.delete("/{id}/")
def inactivate_metodo_pago(id: int, session: Session = Depends(get_session)):
    if not id:
        raise HTTPException(status_code=404, detail="No se encuentra un método de pago asociado a la ID suministrada")
    metodo_pago = session.get(MetodoPago, id)
    if not metodo_pago:
        raise HTTPException(status_code=404, detail="No se encuentra ningún método de pago relacionado a la ID suministrada")
    if metodo_pago.estado:
        raise HTTPException(status_code=400, detail="El método de pago ya se encuentra inactivo")
    metodo_pago.estado = False
    session.commit()
    session.refresh(metodo_pago)
    return {"message":f"El método de pago {metodo_pago.nombre} fue inactivado de forma exitosa", "detail":metodo_pago}

@router.patch("/{id}/")
def activate_metodo_pago(id: int, session: Session = Depends(get_session)):
    if not id:
        raise HTTPException(status_code=404, detail="No se encuentra un método de pago asociado a la ID suministrada")
    metodo_pago = session.get(MetodoPago, id)
    if not metodo_pago:
        raise HTTPException(status_code=404, detail="No se encuentra ningún método de pago relacionado a la ID suministrada")
    if not metodo_pago.estado:
        raise HTTPException(status_code=400, detail="El método de pago ya se encuentra inactivo")
    metodo_pago.estado = True
    session.commit()
    session.refresh(metodo_pago)
    return {"message":f"Método de pago {metodo_pago.nombre} activado de forma exitosa", "detail":metodo_pago}