from __future__ import annotations

import hashlib
import os
from pathlib import Path

from fastapi import UploadFile

from ..core.config import settings


def save_upload(document_id: str, upload: UploadFile) -> tuple[str, int, str]:
    base_path = Path(settings.storage_path) / "documents" / document_id
    base_path.mkdir(parents=True, exist_ok=True)
    filename = Path(upload.filename or "uploaded.bin").name
    target = base_path / filename
    size = 0
    hasher = hashlib.sha256()
    with target.open("wb") as handle:
        while True:
            chunk = upload.file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            hasher.update(chunk)
            handle.write(chunk)
    return str(target), size, hasher.hexdigest()


def save_questionnaire(project_id: str, upload: UploadFile) -> tuple[str, int]:
    base_path = Path(settings.questionnaire_output_path) / project_id
    base_path.mkdir(parents=True, exist_ok=True)
    filename = Path(upload.filename or "questionnaire.pdf").name
    target = base_path / filename
    size = 0
    with target.open("wb") as handle:
        while True:
            chunk = upload.file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            handle.write(chunk)
    return str(target), size


def ensure_storage_dirs() -> None:
    os.makedirs(settings.storage_path, exist_ok=True)
