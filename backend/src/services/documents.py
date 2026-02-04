from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.db_models import Document


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
