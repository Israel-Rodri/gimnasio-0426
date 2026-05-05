from sqlmodel import SQLModel, Field

class RutinasPlanesLink(SQLModel, table=True):
    __tablename__ = "rutinas_planes_link"
    rutina_id: int | None = Field(default=None, foreign_key="rutinas.id", primary_key=True)
    plan_id: int | None = Field(default=None, foreign_key="planes.id", primary_key=True)