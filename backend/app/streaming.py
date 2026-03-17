import json
from typing import Any


def _json_default(value: Any) -> str:
    return str(value)


def to_ndjson_line(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, default=_json_default, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )
