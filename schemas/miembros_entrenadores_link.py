from sqlmodel import SQLModel

class CreateMiembroEntrenadorLink(SQLModel):
    miembro_ci: int
    entrenador_ci: int