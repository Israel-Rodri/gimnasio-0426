from sqlmodel import SQLModel

class CreateRutinasPlanesLink(SQLModel):
    rutina_id: int
    plan_id: int