from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"] = Field(
        ...,
        description="Role of the message sender.",
    )
    content: str = Field(..., min_length=1, description="Message text content.")


class ChatStreamRequest(BaseModel):
    messages: list[ChatMessage] = Field(
        ...,
        min_length=1,
        description="Conversation thread sent by the client for a stateless run.",
    )


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app: str
