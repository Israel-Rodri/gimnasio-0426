from sqlmodel import SQLModel, Field

class MiembrosEntrenadoresLink(SQLModel, table=True):
    __tablename__ = "miembros_entrenadores_link"
    miembro_id: int | None = Field(default=None, foreign_key="miembros.id", primary_key=True)
    entrenador_id: int | None = Field(default=None, foreign_key="entrenadores.id", primary_key=True)