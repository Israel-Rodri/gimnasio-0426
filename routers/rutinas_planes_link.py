from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from database import get_session
from models.rutinas_planes_link import RutinasPlanesLink
from models.rutinas import Rutina
from models.planes import Plan
from schemas.rutinas_planes_link import CreateRutinasPlanesLink

router = APIRouter(prefix="/rutinas-planes", tags=["Enlace Rutinas Planes"])

@router.post("/")
def link_rutinas_planes(data: CreateRutinasPlanesLink, session: Session = Depends(get_session)):
    if not data:
        raise HTTPException(status_code=400, detail="Debe proporcionar todos los datos solicitados")
    rutina = session.get(Rutina, data.rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"No se encuentra una rutina asociada a la ID {data.rutina_id}")
    plan = session.get(Plan, data.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No se encuentra un plan asociado a la ID {data.plan_id}")
    existing_link = session.exec(
        select(RutinasPlanesLink).where(
            RutinasPlanesLink.rutina_id == data.rutina_id,
            RutinasPlanesLink.plan_id == data.plan_id
        )
    ).first()
    if existing_link:
        raise HTTPException(status_code=400, detail=f"Ya existe una relación entre la rutina {rutina.nombre} y el plan {plan.nombre}")
    link = RutinasPlanesLink(
        rutina_id = data.rutina_id,
        plan_id = data.plan_id
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    return {"message":f"Rutina {rutina.nombre} asociada de forma exitosa al plan {plan.nombre}", "detail":link}

router.get("/", response_model=list[RutinasPlanesLink])
def get_all_rutinas_planes_link(session: Session = Depends(get_session)):
    link = session.exec(select(RutinasPlanesLink)).all()
    if not link:
        raise HTTPException(status_code=404, detail="No existen relaciones registradas entre rutinas y planes")
    return link