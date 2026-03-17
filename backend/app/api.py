import logging
from functools import lru_cache
from typing import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.agent import AgentService
from app.auth import AuthenticatedUser, require_authenticated_user
from app.config import Settings, get_settings
from app.schemas import ChatStreamRequest, HealthResponse
from app.streaming import to_ndjson_line


router = APIRouter()
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_cached_settings() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_agent_service() -> AgentService:
    settings = get_cached_settings()
    return AgentService(settings=settings)


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_cached_settings)) -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name)


@router.post("/chat/stream")
async def chat_stream(
    payload: ChatStreamRequest,
    service: AgentService = Depends(get_agent_service),
    _user: AuthenticatedUser = Depends(require_authenticated_user),
) -> StreamingResponse:
    async def stream() -> AsyncIterator[bytes]:
        try:
            async for event in service.stream_events(payload.messages):
                yield to_ndjson_line(event)
        except Exception as exc:
            logger.exception("Streaming error")
            yield to_ndjson_line(
                {
                    "event": "error",
                    "data": {"message": "Agent stream failed", "detail": str(exc)},
                }
            )

    return StreamingResponse(stream(), media_type="application/x-ndjson")
