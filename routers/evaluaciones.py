from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from datetime import date
from database import get_session
from models.evaluaciones import EvaluacionFisica
from models.miembros import Miembro
from models.entrenadores import Entrenador
from schemas.evaluaciones import CreateEvaluacionFisica, UpdateEvaluacionFisica, UpdateEvaluacionFisicaOptional, EvaluacionFisicaResponse
from schemas.base import MessageResponse

router = APIRouter(prefix="/evaluacion-fisica", tags=["Evaluaciones Fisicas"])

def calcular_imc(talla: float, peso: float) -> float:
    return peso / (talla ** 2)

def calcular_estado_imc(imc: float) -> str:
    if imc < 18.5:
        return "Bajo peso"
    elif imc <= 24.9:
        return "Peso Normal"
    elif imc <= 29.9:
        return "Sobrepeso"
    else:
        return "Obesidad"

@router.post("/", response_model=MessageResponse[EvaluacionFisicaResponse])
def create_evaluacion(data: CreateEvaluacionFisica, session: Session = Depends(get_session)):
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == data.miembro_ci
        )
    ).first()
    if not miembro or not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro con la cedula {data.miembro_ci} no se encuentra registrado o no se encuentra activo")
    entrenador = session.get(Entrenador, data.entrenador_id)
    if not entrenador or not entrenador.estado:
        raise HTTPException(status_code=400, detail=f"El entrenador con la ID {data.entrenador_id} no se encuentra registrado o no se encuentra activo")
    existing = session.exec(
        select(EvaluacionFisica).where(
            EvaluacionFisica.fecha_evaluacion == data.fecha_evaluacion,
            EvaluacionFisica.miembro_id == miembro.id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Ya existe una evaluacion realizada al miembro {miembro.nombre} {miembro.apellido} en la fecha {data.fecha_evaluacion}")
    imc = calcular_imc(data.talla, data.peso)
    estado_imc = calcular_estado_imc(imc)
    evaluacion = EvaluacionFisica(
        peso = data.peso,
        talla = data.talla,
        imc = imc,
        estado_imc = estado_imc,
        medidas = data.medidas,
        observaciones = data.observaciones,
        fecha_evaluacion = data.fecha_evaluacion,
        miembro_id = miembro.id,
        entrenador_id = data.entrenador_id
    )
    session.add(evaluacion)
    session.commit()
    session.refresh(evaluacion)
    return {"message":"Evaluacion fisica registrada de forma exitosa", "detail":evaluacion}

@router.get("/", response_model=list[EvaluacionFisicaResponse])
def get_active_evaluaciones(session: Session = Depends(get_session)):
    evaluacion = session.exec(select(EvaluacionFisica).where(EvaluacionFisica.estado==True)).all()
    if not evaluacion:
        raise HTTPException(status_code=404, detail="No existe ninguna evaluacion fisica registrada")
    return evaluacion

@router.get("/all/", response_model=list[EvaluacionFisicaResponse])
def get_all_evaluaciones(session: Session = Depends(get_session)):
    evaluacion = session.exec(select(EvaluacionFisica)).all()
    if not evaluacion:
        raise HTTPException(status_code=404, detail="No se encuentran evaluaciones registradas")
    return evaluacion

@router.get("/filter/", response_model=list[EvaluacionFisicaResponse])
def filter_evaluacion(
    miembro_ci: Optional[int] = Query(default=None),
    fecha: Optional[date] = Query(default=None),
    limite: int = 10,
    session: Session = Depends(get_session)
):
    if not miembro_ci and not fecha:
        raise HTTPException(status_code=400, detail="Debe suministrar por lo menos uno de los campos para filtrar")
    query = select(EvaluacionFisica).where(EvaluacionFisica.estado == True)
    if miembro_ci:
        miembro = session.exec(select(Miembro).where(Miembro.ci == miembro_ci)).first()
        if miembro:
            query = query.where(EvaluacionFisica.miembro_id == miembro.id)
        else:
            return []
    if fecha:
        query = query.where(EvaluacionFisica.fecha_evaluacion == fecha)
    query = query.limit(limite)
    return session.exec(query).all()

@router.patch("/update/{evaluacion_id}/", response_model=MessageResponse[EvaluacionFisicaResponse])
def patch_evaluacion(evaluacion_id: int, data: UpdateEvaluacionFisicaOptional, session: Session = Depends(get_session)):
    evaluacion = session.get(EvaluacionFisica, evaluacion_id)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="No se encuentra la evaluacion solicitada")
    if not evaluacion.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar una evaluacion inactiva")
    if data.peso is not None:
        evaluacion.peso = data.peso
        evaluacion.imc = calcular_imc(evaluacion.talla, data.peso)
        evaluacion.estado_imc = calcular_estado_imc(evaluacion.imc)
    if data.talla is not None:
        evaluacion.talla = data.talla
        evaluacion.imc = calcular_imc(data.talla, evaluacion.peso)
        evaluacion.estado_imc = calcular_estado_imc(evaluacion.imc)
    if data.medidas is not None:
        evaluacion.medidas = data.medidas
    if data.observaciones is not None:
        evaluacion.observaciones = data.observaciones
    if data.fecha_evaluacion is not None:
        evaluacion.fecha_evaluacion = data.fecha_evaluacion
    session.commit()
    session.refresh(evaluacion)
    return {"message":"Evaluacion actualizada", "detail":evaluacion}

@router.put("/update/{evaluacion_id}/", response_model=MessageResponse[EvaluacionFisicaResponse])
def put_evaluacion(evaluacion_id: int, data: UpdateEvaluacionFisica, session: Session = Depends(get_session)):
    evaluacion = session.get(EvaluacionFisica, evaluacion_id)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="No se encuentra una evaluacion registrada con la ID suministrada")
    if not evaluacion.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar una evaluacion inactiva")
    evaluacion.peso = data.peso
    evaluacion.talla = data.talla
    imc = calcular_imc(data.talla, data.peso)
    evaluacion.imc = imc
    evaluacion.estado_imc = calcular_estado_imc(imc)
    evaluacion.medidas = data.medidas
    evaluacion.observaciones = data.observaciones
    evaluacion.fecha_evaluacion = data.fecha_evaluacion
    session.commit()
    session.refresh(evaluacion)
    return {"message":"La evaluacion ha sido actualizada de forma exitosa", "detail":evaluacion}

@router.delete("/{evaluacion_id}/", response_model=MessageResponse[EvaluacionFisicaResponse])
def inactivate_evaluacion(evaluacion_id: int, session: Session = Depends(get_session)):
    evaluacion = session.get(EvaluacionFisica, evaluacion_id)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="No existe una evaluacion asociada a la ID suministrada")
    if not evaluacion.estado:
        raise HTTPException(status_code=400, detail="La evaluacion ya se encuentra inactiva")
    evaluacion.estado = False
    session.commit()
    session.refresh(evaluacion)
    return {"message":f"Evaluacion con la ID {evaluacion.id} inactivada de forma exitosa", "detail":evaluacion}

@router.patch("/{evaluacion_id}/", response_model=MessageResponse[EvaluacionFisicaResponse])
def activate_evaluacion(evaluacion_id: int, session: Session = Depends(get_session)):
    evaluacion = session.get(EvaluacionFisica, evaluacion_id)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="No existe una evaluacion asociada a la ID suministrada")
    if evaluacion.estado:
        raise HTTPException(status_code=400, detail="La evaluacion ya se encuentra activa")
    evaluacion.estado = True
    session.commit()
    session.refresh(evaluacion)
    return {"message":f"Evaluacion con la ID {evaluacion.id} activada de forma exitosa", "detail":evaluacion}
