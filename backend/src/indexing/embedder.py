from __future__ import annotations

from functools import lru_cache
import logging

from langchain_community.embeddings import FakeEmbeddings, HuggingFaceEmbeddings

from ..core.config import settings

logger = logging.getLogger("embeddings")


@lru_cache(maxsize=1)
def get_embeddings():
    if settings.embeddings_backend.lower() == "fake":
        return FakeEmbeddings(size=384)
    try:
        return HuggingFaceEmbeddings(
            model_name=settings.embedding_model_name,
            model_kwargs={"device": settings.embeddings_device},
        )
    except Exception as exc:  # pragma: no cover
        if settings.embeddings_device.lower() != "cpu":
            logger.warning("Embedding load failed on %s, retrying on cpu.", settings.embeddings_device)
            try:
                return HuggingFaceEmbeddings(
                    model_name=settings.embedding_model_name,
                    model_kwargs={"device": "cpu"},
                )
            except Exception:
                pass
        logger.exception("Embedding load failed, using FakeEmbeddings: %s", exc)
        return FakeEmbeddings(size=384)
