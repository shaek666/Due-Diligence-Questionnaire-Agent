from enum import StrEnum


class ProjectStatus(StrEnum):
    CREATED = "CREATED"
    INDEXING = "INDEXING"
    READY = "READY"
    OUTDATED = "OUTDATED"
    REGENERATING = "REGENERATING"


class AnswerStatus(StrEnum):
    GENERATED = "GENERATED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    MANUAL_UPDATED = "MANUAL_UPDATED"
    MISSING_DATA = "MISSING_DATA"


class RequestStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
