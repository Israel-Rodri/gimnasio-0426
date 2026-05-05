from sqlmodel import SQLModel, Field

class CreateMetodoPago(SQLModel):
    nombre: str = Field(max_length=50, unique=True, index=True)
    estado: bool = Field(default=True)

class UpdateMetodoPago(SQLModel):
    nombre: str = Field(max_length=50)