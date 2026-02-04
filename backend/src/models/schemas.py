from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .enums import AnswerStatus, ProjectStatus, RequestStatus


class Citation(BaseModel):
    document_id: UUID
    page_number: int
    chunk_id: str
    snippet: str
    score: float


class AnswerPayload(BaseModel):
    answer: str
    answerable: bool
    answerability_statement: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    citations: List[Citation] = Field(default_factory=list)


class AnswerRecord(BaseModel):
    id: UUID
    question_id: UUID
    status: AnswerStatus
    ai_answer: Optional[AnswerPayload] = None
    manual_answer: Optional[AnswerPayload] = None
    updated_at: datetime


class QuestionRecord(BaseModel):
    id: UUID
    section_title: str
    order: int
    prompt: str
    answer: Optional[AnswerRecord] = None


class ProjectRecord(BaseModel):
    id: UUID
    name: str
    status: ProjectStatus
    scope: List[UUID]
    created_at: datetime
    updated_at: datetime


class ProjectDetail(ProjectRecord):
    questions: List[QuestionRecord] = Field(default_factory=list)


class RequestRecord(BaseModel):
    id: UUID
    status: RequestStatus
    detail: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DocumentRecord(BaseModel):
    id: UUID
    name: str
    metadata: dict[str, Any]
    path: Optional[str] = None
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: datetime


class RequestIdResponse(BaseModel):
    request_id: UUID


class CreateProjectRequest(BaseModel):
    name: str
    scope: List[UUID] = Field(default_factory=list)
    questionnaire_name: Optional[str] = None
    questionnaire_metadata: dict[str, Any] = Field(default_factory=dict)


class CreateProjectResponse(BaseModel):
    project_id: UUID
    request_id: UUID


class GenerateSingleAnswerRequest(BaseModel):
    project_id: UUID
    question_id: UUID


class GenerateAllAnswersRequest(BaseModel):
    project_id: UUID


class UpdateProjectRequest(BaseModel):
    project_id: UUID
    scope: List[UUID]


class UpdateAnswerRequest(BaseModel):
    answer_id: UUID
    status: AnswerStatus
    manual_answer: Optional[AnswerPayload] = None


class IndexDocumentRequest(BaseModel):
    name: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationResult(BaseModel):
    id: UUID
    project_id: UUID
    metrics: List[dict[str, Any]]
    summary: dict[str, Any]
    created_at: datetime
