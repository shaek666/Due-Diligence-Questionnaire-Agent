from __future__ import annotations

import chromadb
from langchain_community.vectorstores import Chroma

from ..core.config import settings
from .embedder import get_embeddings


def get_chroma(collection_name: str) -> Chroma:
    client = chromadb.PersistentClient(path=settings.chroma_path)
    return Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=get_embeddings(),
    )
