from __future__ import annotations

from datetime import datetime
from typing import Dict
from uuid import UUID, uuid4

from ..models.enums import RequestStatus
from ..models.schemas import RequestRecord


class InMemoryRequestStore:
    def __init__(self) -> None:
        self._requests: Dict[UUID, RequestRecord] = {}

    def create(self) -> RequestRecord:
        request_id = uuid4()
        now = datetime.utcnow()
        record = RequestRecord(
            id=request_id,
            status=RequestStatus.QUEUED,
            detail=None,
            created_at=now,
            updated_at=now,
        )
        self._requests[request_id] = record
        return record

    def update(self, request_id: UUID, status: RequestStatus, detail: str | None = None) -> None:
        record = self._requests.get(request_id)
        if record is None:
            return
        record.status = status
        record.detail = detail
        record.updated_at = datetime.utcnow()

    def get(self, request_id: UUID) -> RequestRecord | None:
        return self._requests.get(request_id)


request_store = InMemoryRequestStore()
