"""Chat completion schemas."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


ChatRole = Literal["system", "user", "assistant", "tool"]


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="allow")

    role: ChatRole
    content: str | list[dict[str, Any]] | None = None


class ChatCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str
    messages: list[ChatMessage] = Field(min_length=1)
    stream: bool = False
    max_tokens: int | None = Field(default=None, gt=0)
    temperature: float | None = Field(default=None, ge=0)
    top_p: float | None = Field(default=None, gt=0, le=1)
    stop: str | list[str] | None = None

    def to_vllm_payload(self) -> dict[str, Any]:
        """Return an OpenAI-compatible payload for vLLM."""
        return self.model_dump(exclude_none=True)
