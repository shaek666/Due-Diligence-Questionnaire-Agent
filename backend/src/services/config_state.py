from __future__ import annotations

import hashlib
import json
from datetime import datetime

from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.db_models import ConfigState


def current_signature() -> str:
    payload = {
        "embeddings_backend": settings.embeddings_backend,
        "embedding_model_name": settings.embedding_model_name,
        "coarse_chunk_size": settings.coarse_chunk_size,
        "coarse_chunk_overlap": settings.coarse_chunk_overlap,
        "citation_chunk_size": settings.citation_chunk_size,
        "citation_chunk_overlap": settings.citation_chunk_overlap,
        "coarse_top_k": settings.coarse_top_k,
        "coarse_fetch_k": settings.coarse_fetch_k,
        "citation_top_k": settings.citation_top_k,
        "llm_model_name": settings.llm_model_name,
        "llm_backend": settings.llm_backend,
        "llm_device": settings.llm_device,
        "llm_torch_dtype": settings.llm_torch_dtype,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return digest


def check_and_update_signature(db: Session) -> tuple[bool, str | None, str]:
    signature = current_signature()
    state = db.query(ConfigState).filter(ConfigState.key == "pipeline_signature").one_or_none()
    if state is None:
        db.add(
            ConfigState(
                key="pipeline_signature",
                value=signature,
                updated_at=datetime.utcnow(),
            )
        )
        db.flush()
        return False, None, signature
    if state.value != signature:
        previous = state.value
        state.value = signature
        state.updated_at = datetime.utcnow()
        db.add(state)
        db.flush()
        return True, previous, signature
    return False, state.value, signature
