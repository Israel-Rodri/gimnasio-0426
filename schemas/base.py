from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class MessageResponse(BaseModel, Generic[T]):
    message: str
    detail: T
