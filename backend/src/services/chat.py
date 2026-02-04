from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from ..models.db_models import ChatMessage, ChatSession


def create_session(db: Session) -> ChatSession:
    session = ChatSession()
    db.add(session)
    db.flush()
    return session


def get_session(db: Session, session_id: UUID) -> ChatSession | None:
    return db.get(ChatSession, session_id)


def get_or_create_session(db: Session, session_id: UUID | None) -> ChatSession:
    if session_id is None:
        return create_session(db)
    session = get_session(db, session_id)
    if session is None:
        return create_session(db)
    return session


def add_message(
    db: Session,
    session_id: UUID,
    role: str,
    content: str,
    answer_payload: dict | None = None,
) -> ChatMessage:
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        answer_payload=answer_payload,
    )
    db.add(message)
    db.flush()
    return message


def list_messages(db: Session, session_id: UUID) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def list_sessions(db: Session) -> list[ChatSession]:
    return db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()
