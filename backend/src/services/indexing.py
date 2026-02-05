from __future__ import annotations

import logging
from uuid import UUID

from langchain_community.vectorstores.utils import filter_complex_metadata
from sqlalchemy.orm import Session

from ..core.config import settings
from ..indexing.chunking import chunk_pages
from ..indexing.vector_store import get_chroma
from ..models.db_models import Document
from ..services.ingestion import parse_document
from ..services.documents import store_document_pages
from ..services.projects import mark_all_docs_outdated

logger = logging.getLogger("indexing")


def index_document(db: Session, document_id: str) -> None:
    document = db.get(Document, UUID(document_id))
    if document is None or not document.path:
        raise ValueError("Document not found or missing path")
    pages = parse_document(document.path)
    store_document_pages(db, document, pages)
    coarse_store = get_chroma("coarse_retrieval")
    citation_store = get_chroma("citation_chunks")
    for store_name, store in (("coarse_retrieval", coarse_store), ("citation_chunks", citation_store)):
        try:
            store.delete(where={"document_id": str(document.id)})
        except Exception as exc:  # pragma: no cover - defensive delete
            logger.debug("Failed to clear %s for document %s: %s", store_name, document.id, exc)
    coarse_chunks = chunk_pages(
        document_id=str(document.id),
        source_name=document.name,
        pages=pages,
        chunk_size=settings.coarse_chunk_size,
        chunk_overlap=settings.coarse_chunk_overlap,
    )
    citation_chunks = chunk_pages(
        document_id=str(document.id),
        source_name=document.name,
        pages=pages,
        chunk_size=settings.citation_chunk_size,
        chunk_overlap=settings.citation_chunk_overlap,
    )
    if coarse_chunks:
        coarse_chunks = filter_complex_metadata(coarse_chunks)
        coarse_store.add_documents(coarse_chunks)
    if citation_chunks:
        citation_chunks = filter_complex_metadata(citation_chunks)
        citation_store.add_documents(citation_chunks)
    mark_all_docs_outdated(db)
