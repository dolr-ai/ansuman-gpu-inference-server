"""Model listing routes."""

from fastapi import APIRouter

from backend.api.deps import SettingsDep
from backend.schemas.model import ModelInfo, ModelListResponse

router = APIRouter(prefix="/v1/models", tags=["models"])


@router.get("", response_model=ModelListResponse)
async def list_models(settings: SettingsDep) -> ModelListResponse:
    """Return the configured model in OpenAI-compatible list format."""
    return ModelListResponse(data=[ModelInfo(id=settings.vllm_model)])
