import logging

from fastapi import FastAPI

from app.api import get_agent_service, get_cached_settings, router


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


settings = get_cached_settings()
_configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.on_event("startup")
def startup_validation() -> None:
    # Fail fast for config/database/model wiring issues.
    get_agent_service()
