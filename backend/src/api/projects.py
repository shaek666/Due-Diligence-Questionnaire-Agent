from __future__ import annotations

from uuid import UUID

import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..models.schemas import (
    AnswerRecord,
    CreateProjectResponse,
    GenerateAllAnswersRequest,
    GenerateSingleAnswerRequest,
    ProjectDetail,
    ProjectRecord,
    QuestionRecord,
    EvaluationResult,
    DocumentRecord,
    RequestIdResponse,
    RequestRecord,
    ReviewEventRecord,
    UpdateAnswerRequest,
    UpdateProjectRequest,
)
from ..models.db_models import Project, Request
from ..services.documents import create_document, list_documents
from ..services.answers import update_manual_answer
from ..services.projects import create_project, list_projects, update_project_scope
from ..services.requests import create_request, list_requests
from ..storage.db import db_session

router = APIRouter()


def get_db() -> Session:
    with db_session() as session:
        yield session


@router.post("/create-project-async", response_model=CreateProjectResponse)
def create_project_endpoint(
    name: str = Form(...),
    scope: str = Form("[]"),
    questionnaire: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> CreateProjectResponse:
    try:
        raw_scope = json.loads(scope)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid scope JSON: {exc}") from exc
    if not isinstance(raw_scope, list):
        raise HTTPException(status_code=422, detail="Scope must be a JSON list of UUIDs")
    parsed_scope = [UUID(item) for item in raw_scope]
    request = create_request(db, kind="create_project")
    from ..services.files import ensure_storage_dirs, save_questionnaire

    project = create_project(db, name=name, scope=parsed_scope, metadata={})
    ensure_storage_dirs()
    path, size = save_questionnaire(str(project.id), questionnaire)
    project.metadata_ = {
        **(project.metadata_ or {}),
        "questionnaire_path": path,
        "questionnaire_name": questionnaire.filename or "questionnaire",
        "questionnaire_size": size,
    }
    db.add(project)
    db.commit()
    from ..workers.tasks import parse_questionnaire_task

    parse_questionnaire_task.delay(str(request.id), str(project.id))
    return CreateProjectResponse(project_id=project.id, request_id=request.id)


@router.post("/generate-single-answer", response_model=RequestIdResponse)
def generate_single_answer(payload: GenerateSingleAnswerRequest, db: Session = Depends(get_db)) -> RequestIdResponse:
    request = create_request(db, kind="generate_single_answer")
    from ..workers.tasks import generate_single_answer_task

    generate_single_answer_task.delay(str(request.id), str(payload.project_id), str(payload.question_id))
    return RequestIdResponse(request_id=request.id)


@router.post("/generate-all-answers", response_model=RequestIdResponse)
def generate_all_answers(payload: GenerateAllAnswersRequest, db: Session = Depends(get_db)) -> RequestIdResponse:
    request = create_request(db, kind="generate_all_answers")
    from ..workers.tasks import generate_all_answers_task

    generate_all_answers_task.delay(str(request.id), str(payload.project_id))
    return RequestIdResponse(request_id=request.id)


@router.post("/update-project-async", response_model=RequestIdResponse)
def update_project(payload: UpdateProjectRequest, db: Session = Depends(get_db)) -> RequestIdResponse:
    project = update_project_scope(db, payload.project_id, payload.scope)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    request = create_request(db, kind="update_project")
    db.commit()
    from ..workers.tasks import parse_questionnaire_task

    parse_questionnaire_task.delay(str(request.id), str(project.id))
    return RequestIdResponse(request_id=request.id)


@router.post("/update-answer")
def update_answer(payload: UpdateAnswerRequest, db: Session = Depends(get_db)) -> dict:
    updated = update_manual_answer(db, payload.answer_id, payload.status, payload.manual_answer)
    if updated is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    return {"status": "updated"}


@router.post("/evaluate-project-async", response_model=RequestIdResponse)
def evaluate_project_async(project_id: UUID, db: Session = Depends(get_db)) -> RequestIdResponse:
    request = create_request(db, kind="evaluate_project")
    db.commit()
    from ..workers.tasks import evaluate_project_task

    evaluate_project_task.delay(str(request.id), str(project_id))
    return RequestIdResponse(request_id=request.id)


@router.get("/get-evaluation", response_model=EvaluationResult)
def get_evaluation(evaluation_id: UUID, db: Session = Depends(get_db)) -> EvaluationResult:
    from ..models.db_models import EvaluationRun

    run = db.get(EvaluationRun, evaluation_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return EvaluationResult(
        id=run.id,
        project_id=run.project_id,
        metrics=run.metrics,
        summary=run.summary,
        created_at=run.created_at,
    )


@router.get("/list-evaluations", response_model=list[EvaluationResult])
def list_evaluations(project_id: UUID, db: Session = Depends(get_db)) -> list[EvaluationResult]:
    from ..models.db_models import EvaluationRun

    runs = db.query(EvaluationRun).filter(EvaluationRun.project_id == project_id).all()
    return [
        EvaluationResult(
            id=run.id,
            project_id=run.project_id,
            metrics=run.metrics,
            summary=run.summary,
            created_at=run.created_at,
        )
        for run in runs
    ]


@router.get("/get-project-info", response_model=ProjectDetail)
def get_project_info(project_id: UUID, db: Session = Depends(get_db)) -> ProjectDetail:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    questions = []
    for question in project.questions:
        answer = question.answers[0] if question.answers else None
        questions.append(
            QuestionRecord(
                id=question.id,
                section_title=question.section_title,
                order=question.order,
                prompt=question.prompt,
                answer=AnswerRecord(
                    id=answer.id,
                    question_id=answer.question_id,
                    status=answer.status,
                    ai_answer=answer.ai_answer,
                    manual_answer=answer.manual_answer,
                    updated_at=answer.updated_at,
                )
                if answer
                else None,
            )
        )
    return ProjectDetail(
        id=project.id,
        name=project.name,
        status=project.status,
        scope=[UUID(item) for item in project.scope],
        created_at=project.created_at,
        updated_at=project.updated_at,
        questions=questions,
    )


@router.get("/get-project-status", response_model=ProjectRecord)
def get_project_status(project_id: UUID, db: Session = Depends(get_db)) -> ProjectRecord:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectRecord(
        id=project.id,
        name=project.name,
        status=project.status,
        scope=[UUID(item) for item in project.scope],
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("/list-projects", response_model=list[ProjectRecord])
def list_all_projects(db: Session = Depends(get_db)) -> list[ProjectRecord]:
    projects = list_projects(db)
    return [
        ProjectRecord(
            id=project.id,
            name=project.name,
            status=project.status,
            scope=[UUID(item) for item in project.scope],
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
        for project in projects
    ]


@router.post("/index-document-async", response_model=RequestIdResponse)
def index_document(
    name: str = Form(...),
    metadata: str = Form("{}"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> RequestIdResponse:
    try:
        parsed_meta = json.loads(metadata) if metadata else {}
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid metadata JSON: {exc}") from exc
    if not isinstance(parsed_meta, dict):
        raise HTTPException(status_code=422, detail="Metadata must be a JSON object")
    request = create_request(db, kind="index_document")
    document = create_document(db, name=name, metadata=parsed_meta)
    from ..services.files import ensure_storage_dirs, save_upload
    from ..services.documents import update_document_file

    ensure_storage_dirs()
    path, size = save_upload(str(document.id), file)
    update_document_file(db, document=document, path=path, mime_type=file.content_type, size_bytes=size)
    db.commit()
    from ..workers.tasks import index_document_task

    index_document_task.delay(str(request.id), str(document.id))
    return RequestIdResponse(request_id=request.id)


@router.get("/list-documents", response_model=list[DocumentRecord])
def list_all_documents(db: Session = Depends(get_db)) -> list[DocumentRecord]:
    documents = list_documents(db)
    return [
        DocumentRecord(
            id=doc.id,
            name=doc.name,
            metadata=doc.metadata_,
            path=doc.path,
            mime_type=doc.mime_type,
            size_bytes=doc.size_bytes,
            created_at=doc.created_at,
        )
        for doc in documents
    ]


@router.get("/get-request-status", response_model=RequestRecord)
def get_request_status(request_id: UUID, db: Session = Depends(get_db)) -> RequestRecord:
    record = db.get(Request, request_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return RequestRecord(
        id=record.id,
        status=record.status,
        detail=record.detail,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get("/list-requests", response_model=list[RequestRecord])
def list_all_requests(db: Session = Depends(get_db)) -> list[RequestRecord]:
    requests = list_requests(db)
    return [
        RequestRecord(
            id=request.id,
            status=request.status,
            detail=request.detail,
            created_at=request.created_at,
            updated_at=request.updated_at,
        )
        for request in requests
    ]


@router.get("/list-review-events", response_model=list[ReviewEventRecord])
def list_review_events(answer_id: UUID, db: Session = Depends(get_db)) -> list[ReviewEventRecord]:
    from ..models.db_models import ReviewEvent

    events = (
        db.query(ReviewEvent)
        .filter(ReviewEvent.answer_id == answer_id)
        .order_by(ReviewEvent.created_at.desc())
        .all()
    )
    return [
        ReviewEventRecord(
            id=event.id,
            answer_id=event.answer_id,
            status=event.status,
            note=event.note,
            created_at=event.created_at,
        )
        for event in events
    ]
