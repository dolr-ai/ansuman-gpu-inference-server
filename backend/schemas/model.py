"""Model API schemas."""

from pydantic import BaseModel


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = 0
    owned_by: str = "yral"


class ModelListResponse(BaseModel):
    object: str = "list"
    data: list[ModelInfo]
