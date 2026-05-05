from sqlmodel import SQLModel, Field

class PagosPlanesLink(SQLModel, table=True):
    __tablename__ = "pagos_planes_link"
    pago_id: int | None = Field(default=None, foreign_key="pagos.id", primary_key=True)
    plan_id: int | None = Field(default=None, foreign_key="planes.id", primary_key=True)