from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from pydantic import EmailStr
from database import get_session
from models.entrenadores import Entrenador
from models.sedes import Sede
from schemas.entrenadores import CreateEntrenador, UpdateEntrenador, UpdateEntrenadorOptional, EntrenadorResponse
from schemas.miembros import MiembroResponse
from schemas.base import MessageResponse

router = APIRouter(prefix="/entrenador", tags=["Entrenadores"])

@router.post("/", response_model=MessageResponse[EntrenadorResponse])
def create_entrenador(data: CreateEntrenador, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Entrenador).where(
            Entrenador.ci == data.ci
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Ya existe un entrenador registrado con la cedula {data.ci}")
    sede = session.get(Sede, data.sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No existe una sede relacionada a la ID suministrada")
    entrenador = Entrenador(
        ci = data.ci,
        nombre = data.nombre,
        apellido = data.apellido,
        especialidad = data.especialidad,
        certificaciones = data.certificaciones,
        telefono = data.telefono,
        email = data.email,
        estado = data.estado,
        sede_id = data.sede_id
    )
    session.add(entrenador)
    session.commit()
    session.refresh(entrenador)
    return {"message":f"Entrenador {entrenador.nombre} {entrenador.apellido} creado de forma exitosa", "detail":entrenador}

@router.get("/all/", response_model=list[EntrenadorResponse])
def get_entrenador(session: Session = Depends(get_session)):
    entrenador = session.exec(select(Entrenador)).all()
    if not entrenador:
        raise HTTPException(status_code=404, detail="No existen entrenadores registrados")
    return entrenador

@router.get("/", response_model=list[EntrenadorResponse])
def get_active_entrenadores(session: Session = Depends(get_session)):
    entrenador = session.exec(select(Entrenador).where(Entrenador.estado == True)).all()
    if not entrenador:
        raise HTTPException(status_code=404, detail="No existen entrenadores registrados o activos")
    return entrenador

@router.get("/filter/", response_model=list[EntrenadorResponse])
def filter_entrenador(
    entrenador_ci: Optional[int] = Query(default=None),
    entrenador_nombre: Optional[str] = Query(default=None),
    entrenador_apellido: Optional[str] = Query(default=None),
    entrenador_especialidad: Optional[str] = Query(default=None),
    entrenador_email: Optional[EmailStr] = Query(default=None),
    limite: int = 10,
    session: Session = Depends(get_session)
):
    if not entrenador_ci and not entrenador_nombre and not entrenador_apellido and not entrenador_especialidad and not entrenador_email:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos uno de los campos para filtrar")
    query = select(Entrenador).where(Entrenador.estado==True)
    if entrenador_ci:
        query = query.where(Entrenador.ci == entrenador_ci)
    if entrenador_nombre:
        query = query.where(Entrenador.nombre.ilike(f"%{entrenador_nombre}%"))
    if entrenador_apellido:
        query = query.where(Entrenador.apellido.ilike(f"%{entrenador_apellido}%"))
    if entrenador_especialidad:
        query = query.where(Entrenador.especialidad.ilike(f"%{entrenador_especialidad}%"))
    if entrenador_email:
        query = query.where(Entrenador.email.ilike(f"%{entrenador_email}%"))
    query = query.limit(limite)
    return session.exec(query).all()

@router.get("/{entrenador_ci}/", response_model=MessageResponse[EntrenadorResponse])
def get_entrenador_by_ci(entrenador_ci: int, session: Session = Depends(get_session)):
    entrenador = session.exec(
        select(Entrenador).where(Entrenador.ci == entrenador_ci)
    ).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail=f"No se encuentra ningun entrenador con la cedula {entrenador_ci}")
    return {"message": f"Entrenador {entrenador.nombre} {entrenador.apellido} encontrado de forma exitosa", "detail": entrenador}

@router.get("/{entrenador_ci}/miembros/", response_model=list[MiembroResponse])
def get_miembros_by_entrenador(entrenador_ci: int, session: Session = Depends(get_session)):
    entrenador = session.exec(
        select(Entrenador).where(
            Entrenador.ci == entrenador_ci
        )
    ).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail=f"No existe un entrenador con la cedula {entrenador_ci}")
    return entrenador.miembros

@router.put("/update/{entrenador_ci}/", response_model=MessageResponse[EntrenadorResponse])
def put_entrenador(entrenador_ci: int, data: UpdateEntrenador, session: Session = Depends(get_session)):
    entrenador = session.exec(select(Entrenador).where(Entrenador.ci==entrenador_ci)).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail=f"No existe ningun entrenador asociado a la CI {entrenador_ci}")
    if not entrenador.estado:
        raise HTTPException(status_code=400, detail=f"El entrenador {entrenador.nombre} se encuentra inactivo")
    nombre = entrenador.nombre
    entrenador.ci = data.ci
    entrenador.nombre = data.nombre
    entrenador.apellido = data.apellido
    entrenador.especialidad = data.especialidad
    entrenador.certificaciones = data.certificaciones
    entrenador.telefono = data.telefono
    entrenador.email = data.email
    entrenador.sede_id = data.sede_id
    session.commit()
    session.refresh(entrenador)
    return {"message":f"El entrenador {nombre} fue actualizado de forma exitosa", "detail":entrenador}

@router.patch("/update/{entrenador_ci}/", response_model=MessageResponse[EntrenadorResponse])
def patch_entrenador(entrenador_ci: int, data: UpdateEntrenadorOptional, session: Session = Depends(get_session)):
    entrenador = session.exec(select(Entrenador).where(Entrenador.ci==entrenador_ci)).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail=f"No existe ningun entrenador asociado a la CI {entrenador_ci}")
    if not entrenador.estado:
        raise HTTPException(status_code=400, detail=f"El entrenador {entrenador.nombre} se encuentra inactivo")
    nombre = entrenador.nombre
    if data.ci is not None:
        entrenador.ci = data.ci
    if data.nombre is not None:
        entrenador.nombre = data.nombre
    if data.apellido is not None:
        entrenador.apellido = data.apellido
    if data.especialidad is not None:
        entrenador.especialidad = data.especialidad
    if data.certificaciones is not None:
        entrenador.certificaciones = data.certificaciones
    if data.telefono is not None:
        entrenador.telefono = data.telefono
    if data.email is not None:
        entrenador.email = data.email
    if data.sede_id is not None:
        entrenador.sede_id = data.sede_id
    session.commit()
    session.refresh(entrenador)
    return {"message":f"El entrenador {nombre} fue actualizado de forma exitosa", "detail":entrenador}

@router.delete("/{entrenador_ci}/", response_model=MessageResponse[EntrenadorResponse])
def inactivate(entrenador_ci: int, session: Session = Depends(get_session)):
    entrenador = session.exec(select(Entrenador).where(Entrenador.ci==entrenador_ci)).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail=f"No existe ningun entrenador asociado a la CI {entrenador_ci}")
    if not entrenador.estado:
        raise HTTPException(status_code=400, detail=f"El entrenador {entrenador.nombre} ya se encuentra inactivo")
    entrenador.estado = False
    session.commit()
    session.refresh(entrenador)
    return {"message":f"El entrenador {entrenador.nombre} fue inactivado de forma exitosa", "detail":entrenador}

@router.patch("/{entrenador_ci}/", response_model=MessageResponse[EntrenadorResponse])
def activate(entrenador_ci: int, session: Session = Depends(get_session)):
    entrenador = session.exec(select(Entrenador).where(Entrenador.ci==entrenador_ci)).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail=f"No existe ningun entrenador asociado a la CI {entrenador_ci}")
    if entrenador.estado:
        raise HTTPException(status_code=400, detail=f"El entrenador {entrenador.nombre} ya se encuentra activo")
    entrenador.estado = True
    session.commit()
    session.refresh(entrenador)
    return {"message":f"El entrenador {entrenador.nombre} fue activado de forma exitosa", "detail":entrenador}
