"""Shared API dependencies."""

from typing import Annotated

from fastapi import Depends

from backend.core.config import Settings, get_settings
from backend.services.vllm.client import VLLMClient


SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_vllm_client(settings: SettingsDep) -> VLLMClient:
    """Build a vLLM client for the current request."""
    return VLLMClient(
        base_url=settings.vllm_base_url,
        timeout_seconds=settings.vllm_timeout_seconds,
    )


VLLMClientDep = Annotated[VLLMClient, Depends(get_vllm_client)]
