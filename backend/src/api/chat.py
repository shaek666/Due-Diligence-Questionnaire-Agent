from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.schemas import (
    ChatMessageRecord,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionRecord,
)
from ..services.chat import add_message, get_or_create_session, list_messages, list_sessions
from ..services.requests import create_request
from ..storage.db import db_session

router = APIRouter()


def get_db() -> Session:
    with db_session() as session:
        yield session


@router.post("/create-chat-session", response_model=ChatSessionRecord)
def create_chat_session(db: Session = Depends(get_db)) -> ChatSessionRecord:
    session = get_or_create_session(db, None)
    return ChatSessionRecord(id=session.id, created_at=session.created_at)


@router.post("/chat-message-async", response_model=ChatMessageResponse)
def chat_message(payload: ChatMessageRequest, db: Session = Depends(get_db)) -> ChatMessageResponse:
    request = create_request(db, kind="chat_message")
    session = get_or_create_session(db, payload.session_id)
    message = add_message(db, session.id, role="user", content=payload.message)
    db.commit()
    from ..workers.tasks import chat_generate_task

    chat_generate_task.delay(str(request.id), str(session.id), str(message.id))
    return ChatMessageResponse(session_id=session.id, request_id=request.id)


@router.get("/list-chat-messages", response_model=list[ChatMessageRecord])
def list_chat_messages(session_id: UUID, db: Session = Depends(get_db)) -> list[ChatMessageRecord]:
    messages = list_messages(db, session_id)
    return [
        ChatMessageRecord(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            content=message.content,
            answer_payload=message.answer_payload,
            created_at=message.created_at,
        )
        for message in messages
    ]


@router.get("/list-chat-sessions", response_model=list[ChatSessionRecord])
def list_chat_sessions(db: Session = Depends(get_db)) -> list[ChatSessionRecord]:
    sessions = list_sessions(db)
    return [ChatSessionRecord(id=session.id, created_at=session.created_at) for session in sessions]
