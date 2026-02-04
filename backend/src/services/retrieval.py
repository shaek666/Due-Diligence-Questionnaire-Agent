from __future__ import annotations

from typing import List, Tuple

from langchain_core.documents import Document

from ..core.config import settings
from ..indexing.vector_store import get_chroma


def retrieve_citations(query: str) -> List[Tuple[Document, float]]:
    coarse_store = get_chroma("coarse_retrieval")
    try:
        coarse_docs = coarse_store.max_marginal_relevance_search(
            query, k=settings.coarse_top_k, fetch_k=settings.coarse_fetch_k
        )
    except Exception:
        coarse_docs = []
    doc_ids = {doc.metadata.get("document_id") for doc in coarse_docs if doc.metadata.get("document_id")}
    citation_store = get_chroma("citation_chunks")
    if doc_ids:
        try:
            return citation_store.similarity_search_with_score(
                query, k=settings.citation_top_k, filter={"document_id": {"$in": list(doc_ids)}}
            )
        except Exception:
            return []
    try:
        return citation_store.similarity_search_with_score(query, k=settings.citation_top_k)
    except Exception:
        return []
