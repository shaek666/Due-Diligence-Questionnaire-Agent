from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.db_models import Request
from ..models.enums import RequestStatus


def create_request(db: Session, kind: str | None = None) -> Request:
    request = Request(status=RequestStatus.QUEUED, kind=kind)
    db.add(request)
    db.flush()
    return request


def update_request(db: Session, request_id: UUID, status: RequestStatus, detail: str | None = None) -> Request | None:
    request = db.get(Request, request_id)
    if request is None:
        return None
    request.status = status
    request.detail = detail
    request.updated_at = datetime.utcnow()
    db.add(request)
    db.flush()
    return request


def list_requests(db: Session) -> list[Request]:
    return db.query(Request).order_by(Request.updated_at.desc()).all()
