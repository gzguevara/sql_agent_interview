from __future__ import annotations

import json
from typing import Any, Iterator, TypedDict

import httpx


class StreamEvent(TypedDict):
    event: str
    data: dict[str, Any]


class BackendStreamError(RuntimeError):
    """Raised when the backend stream cannot be consumed."""


class BackendHTTPError(BackendStreamError):
    """Raised when backend returns a non-2xx response."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Backend HTTP {status_code}: {detail}")


def _build_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def check_health(base_url: str) -> tuple[bool, str]:
    url = _build_url(base_url, "/health")
    try:
        with httpx.Client(timeout=httpx.Timeout(5.0)) as client:
            response = client.get(url)
    except httpx.HTTPError as exc:
        return False, f"Health request failed: {exc}"

    if response.status_code >= 400:
        return False, f"Health check failed: HTTP {response.status_code}"

    try:
        payload = response.json()
    except ValueError:
        return True, "Health check passed (non-JSON response)."

    status = payload.get("status", "unknown")
    app_name = payload.get("app", "unknown-app")
    return True, f"{app_name}: {status}"


def stream_chat_events(
    base_url: str,
    messages: list[dict[str, str]],
    id_token: str | None = None,
) -> Iterator[StreamEvent]:
    url = _build_url(base_url, "/chat/stream")
    headers: dict[str, str] = {}
    if id_token:
        headers["Authorization"] = f"Bearer {id_token}"

    try:
        timeout = httpx.Timeout(connect=10.0, read=None, write=30.0, pool=5.0)
        with httpx.Client(timeout=timeout) as client:
            with client.stream(
                "POST",
                url,
                json={"messages": messages},
                headers=headers,
            ) as response:
                if response.status_code >= 400:
                    detail = response.text.strip() or "No response body."
                    raise BackendHTTPError(response.status_code, detail)

                for raw_line in response.iter_lines():
                    line = raw_line.strip()
                    if not line:
                        continue

                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        yield {
                            "event": "error",
                            "data": {
                                "message": "Malformed NDJSON line.",
                                "detail": line[:500],
                            },
                        }
                        continue

                    if not isinstance(payload, dict):
                        yield {
                            "event": "error",
                            "data": {
                                "message": "Unexpected stream payload type.",
                                "detail": str(type(payload)),
                            },
                        }
                        continue

                    event_name = str(payload.get("event", "")).strip()
                    data = payload.get("data", {})
                    if not isinstance(data, dict):
                        data = {"value": data}

                    if not event_name:
                        yield {
                            "event": "error",
                            "data": {
                                "message": "Missing event name in payload.",
                                "detail": line[:500],
                            },
                        }
                        continue

                    yield {"event": event_name, "data": data}
    except httpx.HTTPError as exc:
        raise BackendStreamError(f"Stream request failed: {exc}") from exc
