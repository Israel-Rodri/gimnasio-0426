from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from datetime import date
from database import get_session
from models.evaluaciones import EvaluacionFisica
from models.miembros import Miembro
from schemas.evaluaciones import CreateEvaluacionFisica, UpdateEvaluacionFisica, UpdateEvaluacionFisicaOptional

router = APIRouter(prefix="/evaluacion-fisica", tags=["Evaluaciones Fisicas"])

def calcular_imc(talla: float, peso: float) -> float:
    imc = peso/(talla**2)
    return imc

def calcular_estado_imc(imc: float) -> str:
    if imc < 18.5:
        return "Bajo peso"
    elif imc >= 18.5 and imc <= 24.9:
        return "Peso Normal"
    elif imc >= 25 and imc <= 29.9:
        return "Sobrepeso"
    else:
        return "Obesidad"

@router.post("/")
def create_evaluacion(data: CreateEvaluacionFisica, session: Session = Depends(get_session)):
    if not data:
        raise HTTPException(status_code=400, detail="Debe suministrar todos los datos solicitados")
    existing = session.exec(
        select(EvaluacionFisica).where(
            EvaluacionFisica.fecha_evaluacion == data.fecha_evaluacion,
            EvaluacionFisica.miembro_ci == data.miembro_ci
        )
    ).first()
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == data.miembro_ci
        )
    ).first()
    if miembro == None or not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro con la cédula {data.miembro_ci} no se encuentra registrado o no se encuentra activo")
    if existing:
        raise HTTPException(status_code=400, detail=f"Ya existe una evaluación realizada al miembro {miembro.nombre} {miembro.apellido} en la fecha {data.fecha_evaluacion}")
    evaluacion = EvaluacionFisica(
        peso = data.peso,
        talla = data.talla,
        imc = calcular_imc(data.talla, data.peso),
        estado_imc = calcular_estado_imc(data.imc),
        medidas = data.medidas,
        observaciones = data.observaciones,
        fecha_evaluacion = data.fecha_evaluacion,
        miembro_id = miembro.id
    )
    session.add(evaluacion)
    session.commit()
    session.refresh(evaluacion)
    return {"message":"Evaluación física registrada de forma exitosa", "detail":evaluacion}

@router.get("/", response_model=list[EvaluacionFisica])
def get_active_evaluaciones(session: Session = Depends(get_session)):
    evaluacion = session.exec(select(EvaluacionFisica).where(EvaluacionFisica.estado==True)).all()
    if not evaluacion:
        raise HTTPException(status_code=404, detail="No existe ninguna evaluación física registrada")
    return evaluacion

@router.get("/all/", response_model=list[EvaluacionFisica])
def get_all_evaluaciones(session: Session = Depends(get_session)):
    evaluacion = session.exec(select(EvaluacionFisica)).all()
    if not evaluacion:
        raise HTTPException(status_code=404, detail="No se encuentran evaluaciones registradas")
    return evaluacion

@router.get("/filter/", response_model=list[EvaluacionFisica])
def filter_evaluacion(
    ci: Optional[int] = Query(default=None),
    fecha: Optional[date] = Query(default=None),
    limite: int = 10,
    session: Session = Depends(get_session)
):
    if not ci and not fecha:
        raise HTTPException(status_code=400, detail="Debe suministrar por lo menos uno de los campos para filtrar")
    query = select(EvaluacionFisica)
    if ci:
        query = query.where(EvaluacionFisica.miembro_ci == ci)
    if fecha:
        query = query.where(EvaluacionFisica.fecha_evaluacion == fecha)
    query.limit(limite)
    return session.exec(query).all()

@router.patch("/update/{id}/")
def patch_evaluacion(id: int, data: UpdateEvaluacionFisicaOptional, session: Session = Depends(get_session)):
    if not id: 
        raise HTTPException(status_code=400, detail="Debe suministrar la ID de la evaluación")
    evaluacion = session.get(EvaluacionFisica, id)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="No se encuentra la evaluación solicitada")
    if data.peso:
        evaluacion.peso = data.peso
        evaluacion.imc = calcular_imc(evaluacion.talla, data.peso)
        evaluacion.estado_imc = calcular_estado_imc(evaluacion.imc)
    if data.talla:
        evaluacion.talla = data.talla
        evaluacion.imc = calcular_imc(data.talla, evaluacion.peso)
        evaluacion.estado_imc = calcular_estado_imc(evaluacion.imc)
    if data.medidas:
        evaluacion.medidas = data.medidas
    if data.observaciones:
        evaluacion.observaciones = data.observaciones
    if data.fecha_evaluacion:
        evaluacion.fecha_evaluacion = data.fecha_evaluacion
    if data.miembro_ci:
        evaluacion.miembro_ci = data.miembro_ci
    session.commit()
    session.refresh(evaluacion)
    return {"message":"Evaluación actualizada", "detail":evaluacion}

@router.put("/update/{id}/")
def put_evaluacion(id: int, data: UpdateEvaluacionFisica, session: Session = Depends(get_session)):
    if not id:
        raise HTTPException(status_code=400, detail="Debe suministrar la ID de la evaluación a actualizar")
    evaluacion = session.get(EvaluacionFisica, id)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="No se encuentra una evaluación registrada con la ID suministrada")
    evaluacion.peso = data.peso
    evaluacion.talla = data.talla
    data.imc = calcular_imc(data.talla, data.peso)
    evaluacion.imc = data.imc
    data.estado_imc = calcular_estado_imc(data.imc)
    evaluacion.estado_imc = data.estado_imc
    evaluacion.medidas = data.medidas
    evaluacion.observaciones = data.observaciones
    evaluacion.fecha_evaluacion = data.fecha_evaluacion
    evaluacion.miembro_ci = data.miembro_ci
    session.commit()
    session.refresh(evaluacion)
    return {"message":"La evaluación ha sdio actualizada de forma exitosa", "detail":evaluacion}

@router.delete("/{id}/")
def inactivate_evaluacion(id: int, session: Session = Depends(get_session)):
    if not id:
        raise HTTPException(status_code=400, detail="Debe suministrar la ID de la evaluacion a inactivar")
    evaluacion = session.get(EvaluacionFisica, id)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="No existe una evaluacion asociada a la ID suministrada")
    if not evaluacion.estado:
        raise HTTPException(status_code=400, detail="La evaluación ya se encuentra inactiva")
    evaluacion.estado = False
    session.commit()
    session.refresh(evaluacion)
    return {"message":f"Evaluación con la ID {evaluacion.id} inactivada de forma exitosa", "detail":evaluacion}

@router.patch("/{id}/")
def activate_evaluacion(id: int, session: Session = Depends(get_session)):
    if not id:
        raise HTTPException(status_code=400, detail="Debe suministrar la ID de la evaluacion a activar")
    evaluacion = session.get(EvaluacionFisica, id)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="No existe una evaluacion asociada a la ID suministrada")
    if evaluacion.estado:
        raise HTTPException(status_code=400, detail="La evaluación ya se encuentra activa")
    evaluacion.estado = True
    session.commit()
    session.refresh(evaluacion)
    return {"message":f"Evaluación con la ID {evaluacion.id} activada de forma exitosa", "detail":evaluacion}