from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ..core.config import settings


def _log_path(request_id: str) -> Path:
    base = Path(settings.storage_path) / "logs" / "requests"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{request_id}.log"


def append_request_log(request_id: str, message: str) -> None:
    try:
        timestamp = datetime.utcnow().isoformat()
        path = _log_path(request_id)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"{timestamp} {message}\n")
    except Exception:
        # Logging must never crash worker tasks.
        return
