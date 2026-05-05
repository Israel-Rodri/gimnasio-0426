from sqlmodel import SQLModel

class CreatePagosPlanesLink(SQLModel):
    pago_id: int
    plan_id: int