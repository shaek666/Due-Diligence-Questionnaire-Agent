from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from ..models.db_models import Document, DocumentPage
from ..services.ingestion import PageText


def create_document(db: Session, name: str, metadata: dict) -> Document:
    document = Document(name=name, metadata_=metadata)
    db.add(document)
    db.flush()
    return document


def update_document_file(
    db: Session,
    document: Document,
    path: str,
    mime_type: str | None,
    size_bytes: int | None,
) -> Document:
    document.path = path
    document.mime_type = mime_type
    document.size_bytes = size_bytes
    db.add(document)
    db.flush()
    return document


def list_documents(db: Session) -> list[Document]:
    return db.query(Document).order_by(Document.created_at.desc()).all()


def find_document_by_hash(
    db: Session, content_hash: str, size_bytes: int | None, exclude_id: uuid.UUID | None = None
) -> Document | None:
    if not content_hash:
        return None
    query = db.query(Document)
    if size_bytes is not None:
        query = query.filter(Document.size_bytes == size_bytes)
    for doc in query.all():
        if exclude_id and doc.id == exclude_id:
            continue
        if (doc.metadata_ or {}).get("content_hash") == content_hash:
            return doc
    return None


def store_document_pages(db: Session, document: Document, pages: list[PageText]) -> None:
    db.query(DocumentPage).filter(DocumentPage.document_id == document.id).delete()
    for page in pages:
        db.add(
            DocumentPage(
                document_id=document.id,
                page_number=page.page_number,
                text=page.text,
                page_width=page.page_width,
                page_height=page.page_height,
            )
        )
    db.flush()
