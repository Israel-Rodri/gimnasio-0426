# Estructura general del directorio routers

**El directorio routers se encarga de almancenar todos los archivos relacionados con la creacion de routers y endpoints especificos de la aplicacion**

## `entrenadores.py`

```
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

@router.get("/all/", response_model=list[Entrenador])
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
```

---

## `evaluaciones.py`

```
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
    entrenador = session.exec(
        select(Entrenador).where(
            Entrenador.ci == data.entrenador_ci
        )
    ).first()
    if not entrenador or not entrenador.estado:
        raise HTTPException(status_code=400, detail=f"El entrenador con la ID {data.entrenador_ci} no se encuentra registrado o no se encuentra activo")
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
        entrenador_id = entrenador.id
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

@router.get("/all/", response_model=list[EvaluacionFisica])
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

@router.get("/{evaluacion_id}/", response_model=MessageResponse[EvaluacionFisicaResponse])
def get_evaluacion_by_id(evaluacion_id: int, session: Session = Depends(get_session)):
    evaluacion = session.get(EvaluacionFisica, evaluacion_id)
    if not evaluacion:
        raise HTTPException(status_code=404, detail=f"No se encuentra una evaluacion registrada con la ID {evaluacion_id}")
    return {"message":"Evaluacion encontrada de forma exitosa", "detail":evaluacion}

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
```

---

## `metodos_pago.py`

```
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

@router.get("/all/", response_model=list[MetodoPago])
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
```

---

## `miembros.py`

```
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from datetime import date
from pydantic import EmailStr
from database import get_session
from models.miembros import Miembro
from models.entrenadores import Entrenador
from models.sedes import Sede
from schemas.miembros import CreateMiembro, UpdateMiembro, UpdateMiembroOptional, MiembroResponse
from schemas.evaluaciones import EvaluacionFisicaResponse
from schemas.planes import PlanResponse
from schemas.pagos import PagoResponse
from schemas.entrenadores import EntrenadorResponse
from schemas.base import MessageResponse

router = APIRouter(prefix="/miembro", tags=["Miembros"])

@router.post("/", response_model=MessageResponse[MiembroResponse])
def create_miembro(data: CreateMiembro, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Miembro).where(
            Miembro.ci == data.ci
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"El miembro con la cedula {data.ci} ya se encuentra registrado")
    sede = session.get(Sede, data.sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail=f"La sede con la ID {data.sede_id} no se encuentra registrada")
    entrenador_id = None
    if data.entrenador_ci is not None:
        entrenador = session.exec(select(Entrenador).where(Entrenador.ci == data.entrenador_ci)).first()
        if not entrenador:
            raise HTTPException(status_code=404, detail=f"No existe un entrenador con la cedula {data.entrenador_ci}")
        entrenador_id = entrenador.id
    miembro = Miembro(
        ci = data.ci,
        nombre = data.nombre,
        apellido = data.apellido,
        fecha_nac = data.fecha_nac,
        telefono = data.telefono,
        email = data.email,
        fecha_inscripcion = data.fecha_inscripcion,
        estado = data.estado,
        entrenador_id = entrenador_id,
        sede_id = data.sede_id
    )
    session.add(miembro)
    session.commit()
    session.refresh(miembro)
    return {"message":f"Miembro {miembro.nombre} {miembro.apellido} creado de forma exitosa", "detail":miembro}

@router.get("/all/", response_model=list[Miembro])
def get_all_miembro(session: Session = Depends(get_session)):
    miembro = session.exec(select(Miembro)).all()
    if not miembro:
        raise HTTPException(status_code=404, detail="No se encuentran miembros registrados")
    return miembro

@router.get("/", response_model=list[MiembroResponse])
def get_active_miembro(session: Session = Depends(get_session)):
    miembro = session.exec(
        select(Miembro).where(
            Miembro.estado == True
        )
    ).all()
    if not miembro:
        raise HTTPException(status_code=404, detail="No se encuentran miembros registrados o activos")
    return miembro

@router.get("/filter/", response_model=list[MiembroResponse])
def filter_miembro(
        miembro_ci: Optional[int] = Query(default=None),
        miembro_nombre: Optional[str] = Query(default=None),
        miembro_apellido: Optional[str] = Query(default=None),
        miembro_email: Optional[EmailStr] = Query(default=None),
        miembro_fecha_insc: Optional[date] = Query(default=None),
        entrenador_id: Optional[int] = Query(default=None),
        sede_id: Optional[int] = Query(default=None),
        limite: int = Query(default=10),
        session: Session = Depends(get_session)
    ):
    if not miembro_ci and not miembro_nombre and not miembro_apellido and not miembro_email and not miembro_fecha_insc and not entrenador_id and not sede_id:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos uno de los campos para filtrar")
    query = select(Miembro).where(Miembro.estado==True)
    if miembro_ci:
        query = query.where(Miembro.ci == miembro_ci)
    if miembro_nombre:
        query = query.where(Miembro.nombre.ilike(f"%{miembro_nombre}%"))
    if miembro_apellido:
        query = query.where(Miembro.apellido.ilike(f"%{miembro_apellido}%"))
    if miembro_email:
        query = query.where(Miembro.email.ilike(f"%{miembro_email}%"))
    if miembro_fecha_insc:
        query = query.where(Miembro.fecha_inscripcion == miembro_fecha_insc)
    if entrenador_id:
        query = query.where(Miembro.entrenador_id == entrenador_id)
    if sede_id:
        query = query.where(Miembro.sede_id == sede_id)
    query = query.limit(limite)
    return session.exec(query).all()

@router.get("/{miembro_ci}/", response_model=MessageResponse[MiembroResponse])
def get_miembro_by_ci(miembro_ci: int, session: Session = Depends(get_session)):
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail="No se encuentra un miembro asociado a la cedula ingresada")
    return {"message": f"Miembro {miembro.nombre} {miembro.apellido} encontrado de forma exitosa", "detail": miembro}

@router.get("/{miembro_ci}/evaluaciones/", response_model=MessageResponse[list[EvaluacionFisicaResponse]])
def get_evaluaciones_miembro(miembro_ci: int, session: Session = Depends(get_session)):
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"El miembro con la cedula {miembro_ci} no se encuentra registrado")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail="El miembro seleccionado no se encuentra activo")
    evaluaciones = miembro.evaluaciones
    if not evaluaciones:
        raise HTTPException(status_code=404, detail=f"El miembro {miembro.nombre} {miembro.apellido} no tiene evaluaciones relacionadas")
    return {"message":f"Evaluaciones del miembro {miembro.nombre} {miembro.apellido}:", "detail":evaluaciones}

@router.get("/{miembro_ci}/planes/", response_model=MessageResponse[list[PlanResponse]])
def get_planes_miembro(miembro_ci: int, session: Session = Depends(get_session)):
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"El miembro con la cedula {miembro_ci} no se encuentra registrado")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail="El miembro seleccionado no se encuentra activo")
    planes = miembro.planes
    if not planes:
        raise HTTPException(status_code=404, detail=f"El miembro {miembro.nombre} {miembro.apellido} no tiene planes relacionados")
    return {"message":f"Planes del miembro {miembro.nombre} {miembro.apellido}:", "detail":planes}

@router.get("/{miembro_ci}/pagos/", response_model=MessageResponse[list[PagoResponse]])
def get_pagos_miembro(miembro_ci: int, session: Session = Depends(get_session)):
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"El miembro con la cedula {miembro_ci} no se encuentra registrado")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail="El miembro seleccionado no se encuentra activo")
    pagos = miembro.pagos
    if not pagos:
        raise HTTPException(status_code=404, detail=f"El miembro {miembro.nombre} {miembro.apellido} no tiene pagos relacionados")
    return {"message":f"Pagos del miembro {miembro.nombre} {miembro.apellido}:", "detail":pagos}

@router.post("/{miembro_ci}/entrenadores/{entrenador_ci}/")
def asociar_entrenador_a_miembro(miembro_ci: int, entrenador_ci: int, session: Session = Depends(get_session)):
    miembro = session.exec(select(Miembro).where(Miembro.ci == miembro_ci)).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No existe un miembro con la cedula {miembro_ci}")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} no se encuentra activo")
    entrenador = session.exec(select(Entrenador).where(Entrenador.ci == entrenador_ci)).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail=f"No existe un entrenador con la cedula {entrenador_ci}")
    if entrenador in miembro.entrenadores:
        raise HTTPException(status_code=400, detail=f"Ya existe una relacion entre el miembro {miembro.nombre} y el entrenador {entrenador.nombre}")
    miembro.entrenadores.append(entrenador)
    session.commit()
    return {"message":f"Entrenador {entrenador.nombre} {entrenador.apellido} asociado de forma exitosa al miembro {miembro.nombre} {miembro.apellido}"}

@router.get("/{miembro_ci}/entrenadores/", response_model=list[EntrenadorResponse])
def get_entrenadores_miembro(miembro_ci: int, session: Session = Depends(get_session)):
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No existe un miembro con la cedula {miembro_ci}")
    return miembro.entrenadores

@router.patch("/update/{miembro_ci}/", response_model=MessageResponse[MiembroResponse])
def patch_miembro(miembro_ci: int, data: UpdateMiembroOptional, session: Session = Depends(get_session)):
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No se encuentra ningun miembro asociado a la cedula {miembro_ci}")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} se encuentra inactivo")
    nombre = miembro.nombre
    if data.ci is not None:
        miembro.ci = data.ci
    if data.nombre is not None:
        miembro.nombre = data.nombre
    if data.apellido is not None:
        miembro.apellido = data.apellido
    if data.fecha_nac is not None:
        miembro.fecha_nac = data.fecha_nac
    if data.telefono is not None:
        miembro.telefono = data.telefono
    if data.email is not None:
        miembro.email = data.email
    if data.entrenador_id is not None:
        miembro.entrenador_id = data.entrenador_id
    if data.sede_id is not None:
        miembro.sede_id = data.sede_id
    session.commit()
    session.refresh(miembro)
    return {"message":f"El miembro {nombre} ha sido actualizado de forma exitosa", "detail":miembro}

@router.put("/update/{miembro_ci}/", response_model=MessageResponse[MiembroResponse])
def put_miembro(miembro_ci: int, data: UpdateMiembro, session: Session = Depends(get_session)):
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No se encuentra ningun miembro asociado a la cedula {miembro_ci}")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} se encuentra inactivo")
    nombre = miembro.nombre
    miembro.ci = data.ci
    miembro.nombre = data.nombre
    miembro.apellido = data.apellido
    miembro.fecha_nac = data.fecha_nac
    miembro.telefono = data.telefono
    miembro.email = data.email
    miembro.entrenador_id = data.entrenador_id
    miembro.sede_id = data.sede_id
    session.commit()
    session.refresh(miembro)
    return {"message":f"El miembro {nombre} ha sido actualizado de forma exitosa", "detail":miembro}

@router.delete("/{miembro_ci}/", response_model=MessageResponse[MiembroResponse])
def inactivate_miembro(miembro_ci: int, session: Session = Depends(get_session)):
    miembro = session.exec(select(Miembro).where(Miembro.ci == miembro_ci)).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No existe un miembro con la cedula {miembro_ci}")
    if not miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} ya se encuentra inactivo")
    miembro.estado = False
    session.commit()
    session.refresh(miembro)
    return {"message":f"Miembro {miembro.nombre} inactivado de forma exitosa", "detail":miembro}

@router.patch("/{miembro_ci}/", response_model=MessageResponse[MiembroResponse])
def activate_miembro(miembro_ci: int, session: Session = Depends(get_session)):
    miembro = session.exec(select(Miembro).where(Miembro.ci == miembro_ci)).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"No existe un miembro con la cedula {miembro_ci}")
    if miembro.estado:
        raise HTTPException(status_code=400, detail=f"El miembro {miembro.nombre} ya se encuentra activo")
    miembro.estado = True
    session.commit()
    session.refresh(miembro)
    return {"message":f"Miembro {miembro.nombre} activado de forma exitosa", "detail":miembro}
```
---

## `pagos.py`

```
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

@router.get("/all/", response_model=list[Pago])
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

@router.put("/update/{pago_id}/", response_model=MessageResponse[PagoResponse])
def put_pago(pago_id: int, data: UpdatePago, session: Session = Depends(get_session)):
    pago = session.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail=f"No se encuentra un pago registrado con la ID {pago_id}")
    if not pago.estado:
        raise HTTPException(status_code=400, detail=f"No se puede actualizar un pago inactivo")
    pago.mensualidades = data.mensualidades
    pago.fecha = data.fecha
    pago.monto = data.monto
    pago.referencia = data.referencia
    pago.metodo_id = data.metodo_id
    session.commit()
    session.refresh(pago)
    return {"message":f"El pago con referencia {pago.referencia} ha sido actualizado de forma exitosa", "detail":pago}

@router.patch("/update/{pago_id}/", response_model=MessageResponse[PagoResponse])
def patch_pago(pago_id: int, data: UpdatePagoOptional, session: Session = Depends(get_session)):
    pago = session.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail=f"No se encuentra un pago registrado con la ID {pago_id}")
    if not pago.estado:
        raise HTTPException(status_code=400, detail=f"No se puede actualizar un pago inactivo")
    if data.mensualidades is not None:
        pago.mensualidades = data.mensualidades
    if data.fecha is not None:
        pago.fecha = data.fecha
    if data.monto is not None:
        pago.monto = data.monto
    if data.referencia is not None:
        pago.referencia = data.referencia
    if data.metodo_id is not None:
        pago.metodo_id = data.metodo_id
    session.commit()
    session.refresh(pago)
    return {"message":f"El pago con referencia {pago.referencia} ha sido actualizado de forma exitosa", "detail":pago}

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
```
---

## `planes.py`

```
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from database import get_session
from models.planes import Plan
from models.miembros import Miembro
from models.rutinas import Rutina
from schemas.planes import CreatePlan, UpdatePlan, UpdatePlanOptional, PlanResponse
from schemas.pagos import PagoResponse
from schemas.rutinas import RutinaResponse
from schemas.base import MessageResponse

router = APIRouter(prefix="/plan", tags=["Planes de Ejercicio"])

@router.post("/", response_model=MessageResponse[PlanResponse])
def create_plan(data: CreatePlan, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Plan).where(
            Plan.nombre == data.nombre,
            Plan.precio == data.precio,
            Plan.beneficios == data.beneficios
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un plan con los datos ingresados")
    miembro = session.exec(
        select(Miembro).where(
            Miembro.ci == data.miembro_ci
        )
    ).first()
    if not miembro:
        raise HTTPException(status_code=404, detail=f"El miembro con la cedula {data.miembro_ci} no se encuentra registrado")
    plan = Plan(
        nombre = data.nombre,
        duracion = data.duracion,
        precio = data.precio,
        beneficios = data.beneficios,
        estado = data.estado,
        miembro_id = miembro.id
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return {"message":f"Plan {plan.nombre} creado de forma exitosa", "detail":plan}

@router.get("/all/", response_model=list[Plan])
def get_all_plan(session: Session = Depends(get_session)):
    plan = session.exec(select(Plan)).all()
    if not plan:
        raise HTTPException(status_code=404, detail="No existe ningun plan de ejercicio registrado")
    return plan

@router.get("/", response_model=list[PlanResponse])
def get_active_plan(session: Session = Depends(get_session)):
    plan = session.exec(select(Plan).where(Plan.estado==True)).all()
    if not plan:
        raise HTTPException(status_code=404, detail="No existe ningun plan de ejercicio o no hay ningun plan de ejercicio activo")
    return plan

@router.get("/filter/", response_model=list[PlanResponse])
def filter_plan(
        nombre: Optional[str] = Query(default=None),
        precio: Optional[float] = Query(default=None),
        limite: int = 10,
        session: Session = Depends(get_session)
    ):
    if not nombre and not precio:
        raise HTTPException(status_code=400, detail="Debe suministrar al menos uno de los campos para filtrar")
    query = select(Plan).where(Plan.estado==True)
    if nombre:
        query = query.where(Plan.nombre.ilike(f"%{nombre}%"))
    if precio:
        query = query.where(Plan.precio == precio)
    query = query.limit(limite)
    return session.exec(query).all()

@router.get("/{plan_id}/", response_model=MessageResponse[PlanResponse])
def get_id_plan(plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No se encuentra un plan asociado a la ID {plan_id}")
    if not plan.estado:
        raise HTTPException(status_code=400, detail=f"El plan {plan.nombre} se encuentra inactivo, activelo para acceder a su informacion")
    return {"message":f"Plan de entrenamiento {plan.nombre} encontrado de forma exitosa", "detail":plan}

@router.get("/{plan_id}/pagos/", response_model=MessageResponse[list[PagoResponse]])
def get_pagos_plan(plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No existe un plan asociado a la ID {plan_id}")
    if not plan.estado:
        raise HTTPException(status_code=400, detail=f"El plan {plan.nombre} se encuentra inactivo, activelo para acceder a su informacion")
    pagos = plan.pagos
    if not pagos:
        raise HTTPException(status_code=404, detail=f"No existen pagos asociados al plan {plan.nombre}")
    return {"message":f"Pagos asociados al plan {plan.nombre}:", "detail":pagos}

@router.post("/{plan_id}/rutinas/{rutina_id}/")
def asociar_rutina_a_plan(plan_id: int, rutina_id: int, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No existe un plan asociado a la ID {plan_id}")
    if not plan.estado:
        raise HTTPException(status_code=400, detail=f"El plan {plan.nombre} se encuentra inactivo")
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"No se encuentra una rutina asociada a la ID {rutina_id}")
    if rutina in plan.rutinas:
        raise HTTPException(status_code=400, detail=f"Ya existe una relacion entre la rutina {rutina.nombre} y el plan {plan.nombre}")
    plan.rutinas.append(rutina)
    session.commit()
    return {"message":f"Rutina {rutina.nombre} asociada de forma exitosa al plan {plan.nombre}"}

@router.get("/{plan_id}/rutinas/", response_model=MessageResponse[list[RutinaResponse]])
def get_rutinas_plan(plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"No existe un plan asociado a la ID {plan_id}")
    if not plan.estado:
        raise HTTPException(status_code=400, detail=f"El plan {plan.nombre} se encuentra inactivo, activelo para acceder a su informacion")
    rutinas = plan.rutinas
    if not rutinas:
        raise HTTPException(status_code=404, detail=f"No existen rutinas asociadas al plan {plan.nombre}")
    return {"message":f"Rutinas asociadas al plan {plan.nombre}:", "detail":rutinas}

@router.put("/update/{plan_id}/", response_model=MessageResponse[PlanResponse])
def put_plan(plan_id: int, data: UpdatePlan, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No existe ningun plan de ejercicio asociado a la ID proporcionada")
    if not plan.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar un plan de ejercicio inactivo")
    nombre = plan.nombre
    plan.nombre = data.nombre
    plan.duracion = data.duracion
    plan.precio = data.precio
    plan.beneficios = data.beneficios
    session.commit()
    session.refresh(plan)
    return {"message":f"El plan de ejercicio {nombre} ha sido actualizado de forma exitosa", "detail":plan}

@router.patch("/update/{plan_id}/", response_model=MessageResponse[PlanResponse])
def patch_plan(plan_id: int, data: UpdatePlanOptional, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No existe un plan asociado a la ID suministrada")
    if not plan.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar un plan inactivo")
    nombre = plan.nombre
    if data.nombre is not None:
        plan.nombre = data.nombre
    if data.duracion is not None:
        plan.duracion = data.duracion
    if data.precio is not None:
        plan.precio = data.precio
    if data.beneficios is not None:
        plan.beneficios = data.beneficios
    session.commit()
    session.refresh(plan)
    return {"message":f"El plan {nombre} fue actualizado de forma exitosa", "detail":plan}

@router.delete("/{plan_id}/", response_model=MessageResponse[PlanResponse])
def inactivate_plan(plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No existe un plan asociado a la ID suministrada")
    if not plan.estado:
        raise HTTPException(status_code=400, detail="El plan ya se encuentra inactivo")
    plan.estado = False
    session.commit()
    session.refresh(plan)
    return {"message":f"El plan {plan.nombre} fue inactivado exitosamente", "detail":plan}

@router.patch("/{plan_id}/", response_model=MessageResponse[PlanResponse])
def activate_plan(plan_id: int, session: Session = Depends(get_session)):
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No existe un plan asociado a la ID suministrada")
    if plan.estado:
        raise HTTPException(status_code=400, detail="El plan ya se encuentra activo")
    plan.estado = True
    session.commit()
    session.refresh(plan)
    return {"message":f"El plan {plan.nombre} fue activado exitosamente", "detail":plan}
```

---

## `rutinas.py`

```
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from database import get_session
from models.rutinas import Rutina
from schemas.rutinas import CreateRutina, UpdateRutina, UpdateRutinaOptional, RutinaResponse
from schemas.planes import PlanResponse
from schemas.base import MessageResponse

router = APIRouter(prefix="/rutina", tags=["Rutinas de Ejercicio"])

@router.post("/", response_model=MessageResponse[RutinaResponse])
def create_rutina(data: CreateRutina, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Rutina).where(
            Rutina.nombre == data.nombre
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Ya existe una rutina registrada con el nombre {data.nombre}")
    rutina = Rutina(
        nombre = data.nombre,
        objetivo = data.objetivo,
        nivel = data.nivel,
        descripcion = data.descripcion,
        duracion_estimada = data.duracion_estimada,
        estado = data.estado
    )
    session.add(rutina)
    session.commit()
    session.refresh(rutina)
    return {"message":f"Rutina {rutina.nombre} creada de forma exitosa", "detail":rutina}

@router.get("/all/", response_model=list[Rutina])
def get_all_rutina(session: Session = Depends(get_session)):
    rutina = session.exec(select(Rutina)).all()
    if not rutina:
        raise HTTPException(status_code=404, detail="No existen rutinas de ejercicio registradas")
    return rutina

@router.get("/", response_model=list[RutinaResponse])
def get_active_rutina(session: Session = Depends(get_session)):
    rutina = session.exec(
        select(Rutina).where(
            Rutina.estado == True
        )
    ).all()
    if not rutina:
        raise HTTPException(status_code=404, detail="No existen rutinas registradas o no existen rutinas activas")
    return rutina

@router.get("/filter/", response_model=list[RutinaResponse])
def filter_rutina(
    rutina_nombre: Optional[str] = Query(default=None),
    rutina_objetivo: Optional[str] = Query(default=None),
    rutina_nivel: Optional[str] = Query(default=None),
    rutina_duracion: Optional[float] = Query(default=None),
    limite: int = 10,
    session: Session = Depends(get_session)
):
    if not rutina_nombre and not rutina_objetivo and not rutina_nivel and not rutina_duracion:
        raise HTTPException(status_code=400, detail="Es necesario suministrar al menos un campo para filtrar")
    query = select(Rutina).where(Rutina.estado == True)
    if rutina_nombre:
        query = query.where(Rutina.nombre.ilike(f"%{rutina_nombre}%"))
    if rutina_objetivo:
        query = query.where(Rutina.objetivo.ilike(f"%{rutina_objetivo}%"))
    if rutina_nivel:
        query = query.where(Rutina.nivel.ilike(f"%{rutina_nivel}%"))
    if rutina_duracion:
        query = query.where(Rutina.duracion_estimada == rutina_duracion)
    query = query.limit(limite)
    return session.exec(query).all()

@router.get("/{rutina_id}/", response_model=MessageResponse[RutinaResponse])
def get_rutina_by_id(rutina_id: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"No existe una rutina asociada a la ID {rutina_id}")
    return {"message": f"Rutina {rutina.nombre} encontrada de forma exitosa", "detail": rutina}

@router.get("/{rutina_id}/planes/", response_model=MessageResponse[list[PlanResponse]])
def get_planes_rutina(rutina_id: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail=f"No existe una rutina asociada a la ID {rutina_id}")
    if not rutina.estado:
        raise HTTPException(status_code=400, detail=f"La rutina {rutina.nombre} no se encuentra activa, activela para acceder a su informacion")
    planes = rutina.planes
    if not planes:
        raise HTTPException(status_code=404, detail=f"La rutina {rutina.nombre} no tiene planes asociados")
    return {"message":f"Planes asociados a la rutina {rutina.nombre}:", "detail":planes}

@router.patch("/update/{rutina_id}/", response_model=MessageResponse[RutinaResponse])
def patch_rutina(rutina_id: int, data: UpdateRutinaOptional, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail="No existe una rutina asociada a la ID suministrada")
    if not rutina.estado:
        raise HTTPException(status_code=400, detail=f"La rutina {rutina.nombre} se encuentra inactiva")
    nombre = rutina.nombre
    if data.nombre is not None:
        rutina.nombre = data.nombre
    if data.objetivo is not None:
        rutina.objetivo = data.objetivo
    if data.nivel is not None:
        rutina.nivel = data.nivel
    if data.descripcion is not None:
        rutina.descripcion = data.descripcion
    if data.duracion_estimada is not None:
        rutina.duracion_estimada = data.duracion_estimada
    session.commit()
    session.refresh(rutina)
    return {"message":f"La rutina {nombre} ha sido actualizada de forma exitosa", "detail":rutina}

@router.put("/update/{rutina_id}/", response_model=MessageResponse[RutinaResponse])
def put_rutina(rutina_id: int, data: UpdateRutina, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail="No existe una rutina asociada a la ID suministrada")
    if not rutina.estado:
        raise HTTPException(status_code=400, detail=f"La rutina {rutina.nombre} se encuentra inactiva")
    nombre = rutina.nombre
    rutina.nombre = data.nombre
    rutina.objetivo = data.objetivo
    rutina.nivel = data.nivel
    rutina.descripcion = data.descripcion
    rutina.duracion_estimada = data.duracion_estimada
    session.commit()
    session.refresh(rutina)
    return {"message":f"La rutina {nombre} ha sido actualizada de forma exitosa", "detail":rutina}

@router.delete("/{rutina_id}/", response_model=MessageResponse[RutinaResponse])
def inactivate_rutina(rutina_id: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail="No existe una rutina asociada a la ID suministrada")
    if not rutina.estado:
        raise HTTPException(status_code=400, detail=f"La rutina {rutina.nombre} ya se encuentra inactiva")
    rutina.estado = False
    session.commit()
    session.refresh(rutina)
    return {"message":f"La rutina {rutina.nombre} ha sido inactivada de forma exitosa", "detail":rutina}

@router.patch("/{rutina_id}/", response_model=MessageResponse[RutinaResponse])
def activate_rutina(rutina_id: int, session: Session = Depends(get_session)):
    rutina = session.get(Rutina, rutina_id)
    if not rutina:
        raise HTTPException(status_code=404, detail="No existe una rutina asociada a la ID suministrada")
    if rutina.estado:
        raise HTTPException(status_code=400, detail=f"La rutina {rutina.nombre} ya se encuentra activa")
    rutina.estado = True
    session.commit()
    session.refresh(rutina)
    return {"message":f"La rutina {rutina.nombre} ha sido activada de forma exitosa", "detail":rutina}
```

---

## `sedes.py`

```
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import Session, select
from typing import Optional
from database import get_session
from models.sedes import Sede
from schemas.sedes import CreateSede, UpdateSede, UpdateSedeOptional, SedeResponse
from schemas.miembros import MiembroResponse
from schemas.entrenadores import EntrenadorResponse
from schemas.base import MessageResponse

router = APIRouter(prefix="/sede", tags=["Sedes"])

@router.post("/", response_model=MessageResponse[SedeResponse])
def create_sede(data: CreateSede, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Sede).where(
            Sede.nombre == data.nombre
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una sede con el nombre ingresado")
    sede = Sede(
        nombre = data.nombre,
        direccion = data.direccion,
        telefono = data.telefono,
        horario = data.horario,
        estado = data.estado
    )
    session.add(sede)
    session.commit()
    session.refresh(sede)
    return {"message":f"Sede {sede.nombre} creada exitosamente", "detail":sede}

@router.get("/all/", response_model=list[Sede])
def get_all_sede(session: Session = Depends(get_session)):
    sede = session.exec(select(Sede)).all()
    if not sede:
        raise HTTPException(status_code=404, detail="No existen sedes registradas")
    return sede

@router.get("/", response_model=list[SedeResponse])
def get_active_sede(session: Session = Depends(get_session)):
    sede = session.exec(select(Sede).where(Sede.estado==True)).all()
    if not sede:
        raise HTTPException(status_code=404, detail="No existen sedes activas")
    return sede

@router.get("/filter/", response_model=list[SedeResponse])
def filter_sede(
        sede_nombre: Optional[str] = Query(None),
        sede_direccion: Optional[str] = Query(None),
        limite: int = 10,
        session: Session = Depends(get_session)
    ):
    if not sede_nombre and not sede_direccion:
        raise HTTPException(status_code=400, detail="Se debe llenar al menos uno de los campos para filtrar")
    query = select(Sede).where(Sede.estado == True)
    if sede_nombre:
        query = query.where(Sede.nombre.ilike(f"%{sede_nombre}%"))
    if sede_direccion:
        query = query.where(Sede.direccion.ilike(f"%{sede_direccion}%"))
    query = query.limit(limite)
    return session.exec(query).all()

@router.get("/{sede_id}/", response_model=MessageResponse[SedeResponse])
def get_id_sede(sede_id: int, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No se encuentra una sede asociada a la ID suministrada")
    if not sede.estado:
        raise HTTPException(status_code=400, detail=f"La sede {sede.nombre} se encuentra inactiva, activela para poder acceder a su informacion")
    return {"message":f"Sede {sede.nombre} encontrada de forma exitosa", "detail":sede}

@router.get("/{sede_id}/miembros/", response_model=MessageResponse[list[MiembroResponse]])
def get_miembros_sede(sede_id: int, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No se encuentra una sede asociada a la ID suministrada")
    if not sede.estado:
        raise HTTPException(status_code=400, detail=f"La sede {sede.nombre} se encuentra inactiva, activela para poder acceder a su informacion")
    miembros = sede.miembros
    if not miembros:
        raise HTTPException(status_code=404, detail=f"No existen miembros asociados a la sede con la ID {sede_id}")
    return {"message":f"Miembros de la sede con la ID {sede_id}", "detail":miembros}

@router.get("/{sede_id}/entrenadores/", response_model=MessageResponse[list[EntrenadorResponse]])
def get_entrenadores_sede(sede_id: int, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No se encuentra una sede asociada a la ID suministrada")
    if not sede.estado:
        raise HTTPException(status_code=400, detail=f"La sede {sede.nombre} se encuentra inactiva, activela para poder acceder a su informacion")
    entrenadores = sede.entrenadores
    if not entrenadores:
        raise HTTPException(status_code=404, detail=f"No existen entrenadores asociados a la sede con la ID {sede_id}")
    return {"message":f"Entrenadores de la sede con la ID {sede_id}", "detail":entrenadores}

@router.put("/update/{sede_id}/", response_model=MessageResponse[SedeResponse])
def put_sede(sede_id: int, data: UpdateSede, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No existe una sede con la id proporcionada")
    if not sede.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar una sede inactiva")
    nombre = sede.nombre
    sede.nombre = data.nombre
    sede.direccion = data.direccion
    sede.telefono = data.telefono
    sede.horario = data.horario
    session.commit()
    session.refresh(sede)
    return {"message":f"Sede {nombre} actualizada de forma exitosa", "detail":sede}

@router.patch("/update/{sede_id}/", response_model=MessageResponse[SedeResponse])
def patch_sede(sede_id: int, data: UpdateSedeOptional, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No existe una sede asociada a la id suministrada")
    if not sede.estado:
        raise HTTPException(status_code=400, detail="No se puede actualizar una sede inactiva")
    if data.nombre is not None:
        sede.nombre = data.nombre
    if data.direccion is not None:
        sede.direccion = data.direccion
    if data.telefono is not None:
        sede.telefono = data.telefono
    if data.horario is not None:
        sede.horario = data.horario
    session.commit()
    session.refresh(sede)
    return {"message":f"Sede {sede.nombre} actualizada de forma correcta", "detail":sede}

@router.delete("/{sede_id}/", response_model=MessageResponse[SedeResponse])
def inactivate_sede(sede_id: int, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No existe una sede con la id suministrada")
    if not sede.estado:
        raise HTTPException(status_code=400, detail=f"La sede {sede.nombre} ya se encuentra inactiva")
    sede.estado = False
    session.commit()
    session.refresh(sede)
    return {"message":f"La sede {sede.nombre} fue inactivada de forma exitosa", "detail":sede}

@router.patch("/{sede_id}/", response_model=MessageResponse[SedeResponse])
def activate_sede(sede_id: int, session: Session = Depends(get_session)):
    sede = session.get(Sede, sede_id)
    if not sede:
        raise HTTPException(status_code=404, detail="No existe una sede con la id suministrada")
    if sede.estado:
        raise HTTPException(status_code=400, detail=f"La sede {sede.nombre} ya se encuentra activa")
    sede.estado = True
    session.commit()
    session.refresh(sede)
    return {"message":f"La sede {sede.nombre} fue activada de forma exitosa", "detail":sede}
```