from __future__ import annotations

import hashlib
import json
from datetime import datetime
import os

from sqlalchemy.orm import Session

from ..models.db_models import ConfigState


def current_signature() -> str:
    payload = {
        "embeddings_backend": os.getenv("EMBEDDINGS_BACKEND", "sentence_transformers"),
        "embedding_model_name": os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"),
        "coarse_chunk_size": int(os.getenv("COARSE_CHUNK_SIZE", "1800")),
        "coarse_chunk_overlap": int(os.getenv("COARSE_CHUNK_OVERLAP", "200")),
        "citation_chunk_size": int(os.getenv("CITATION_CHUNK_SIZE", "800")),
        "citation_chunk_overlap": int(os.getenv("CITATION_CHUNK_OVERLAP", "120")),
        "coarse_top_k": int(os.getenv("COARSE_TOP_K", "6")),
        "coarse_fetch_k": int(os.getenv("COARSE_FETCH_K", "12")),
        "citation_top_k": int(os.getenv("CITATION_TOP_K", "6")),
        "llm_model_name": os.getenv("LLM_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2"),
        "llm_backend": os.getenv("LLM_BACKEND", "transformers"),
        "llm_device": os.getenv("LLM_DEVICE", "cpu"),
        "llm_torch_dtype": os.getenv("LLM_TORCH_DTYPE", "float32"),
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return digest


def check_and_update_signature(db: Session) -> tuple[bool, str | None, str]:
    signature = current_signature()
    state = db.query(ConfigState).filter(ConfigState.key == "pipeline_signature").one_or_none()
    inflight = db.query(ConfigState).filter(ConfigState.key == "regen_inflight").one_or_none()
    if inflight and inflight.value == "1":
        return False, state.value if state else None, signature
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


def set_regen_inflight(db: Session, inflight: bool) -> None:
    state = db.query(ConfigState).filter(ConfigState.key == "regen_inflight").one_or_none()
    value = "1" if inflight else "0"
    if state is None:
        db.add(ConfigState(key="regen_inflight", value=value, updated_at=datetime.utcnow()))
    else:
        state.value = value
        state.updated_at = datetime.utcnow()
        db.add(state)
    db.flush()
