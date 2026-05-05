from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models.miembros_entrenadores_link import MiembrosEntrenadoresLink
from models.miembros import Miembro
from models.entrenadores import Entrenador
from schemas.miembros_entrenadores_link import CreateMiembroEntrenadorLink

router = APIRouter(prefix="/miembros-entrenadores", tags=["Enlace Miembros Entrenadores"])

@router.post("/")
def link_miembros_entrenadores(data: CreateMiembroEntrenadorLink, session: Session = Depends(get_session)):
    if not data:
        raise HTTPException(status_code=400, detail="Debe suministrar todos los datos solicitados")
    entrenador = session.exec(
        select(Entrenador).where(
            Entrenador.ci == data.entrenador_ci
        )
    ).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail=f"No existe un entrenador con la cédula {data.entrenador_ci}")
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == data.miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No existe un miembro con la cédula {data.miembro_ci}")
    existing_link = session.exec(
        select(MiembrosEntrenadoresLink).where(
            MiembrosEntrenadoresLink.miembro_id == miembro.id,
            MiembrosEntrenadoresLink.entrenador_id == entrenador.id
        )
    ).first()
    if existing_link:
        raise HTTPException(status_code=400, detail=f"Ya existe una relacion entre el miembro {data.miembro_ci} y el entrenador {data.entrenador_ci}")
    link = MiembrosEntrenadoresLink(
        miembro_id = miembro.id,
        entrenador_id = entrenador.id
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    return {"message":f"Entrenador con la cédula {data.entrenador_ci} relacionado con el miembro con la cédula {data.miembro_ci} de forma exitosa"}

@router.get("/", response_model=list[MiembrosEntrenadoresLink])
def get_all_miembros_entrenadores_link(session: Session = Depends(get_session)):
    link = session.exec(select(MiembrosEntrenadoresLink)).all()
    if not link:
        raise HTTPException(status_code=404, detail="No hay relaciones existentes entre miembros y entrenadores")
    return link