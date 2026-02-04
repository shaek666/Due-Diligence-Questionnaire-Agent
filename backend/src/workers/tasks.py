from __future__ import annotations

from uuid import UUID
import logging

from .celery_app import celery_app
from ..models.enums import RequestStatus
from ..storage.db import db_session
from ..services.indexing import index_document
from ..services.requests import update_request
from ..services.config_state import set_regen_inflight
from ..models.db_models import Project, Question, Document
from ..models.enums import ProjectStatus
from ..services.answers import generate_answer, upsert_ai_answer
from ..services.evaluation import evaluate_project
from ..services.questionnaire import parse_questionnaire_pdf
from ..services.questions import get_questions_for_project, store_questions
from ..services.projects import set_project_status

logger = logging.getLogger("workers")

def _set_status(request_id: UUID, status: RequestStatus, detail: str | None = None) -> None:
    with db_session() as db:
        update_request(db, request_id=request_id, status=status, detail=detail)


@celery_app.task(name="index_document")
def index_document_task(request_id: str, document_id: str) -> None:
    request_uuid = UUID(request_id)
    logger.info("index_document.start request=%s document=%s", request_id, document_id)
    _set_status(request_uuid, RequestStatus.RUNNING)
    try:
        with db_session() as db:
            index_document(db, document_id)
        _set_status(request_uuid, RequestStatus.SUCCEEDED)
        logger.info("index_document.success request=%s document=%s", request_id, document_id)
    except Exception as exc:  # pragma: no cover - explicit task failure capture
        _set_status(request_uuid, RequestStatus.FAILED, detail=str(exc))
        logger.exception("index_document.failed request=%s document=%s", request_id, document_id)
        raise


@celery_app.task(name="parse_questionnaire")
def parse_questionnaire_task(request_id: str, project_id: str) -> None:
    request_uuid = UUID(request_id)
    logger.info("parse_questionnaire.start request=%s project=%s", request_id, project_id)
    _set_status(request_uuid, RequestStatus.RUNNING)
    try:
        with db_session() as db:
            project = db.get(Project, UUID(project_id))
            if project is None:
                raise ValueError("Project not found")
            set_project_status(db, project.id, ProjectStatus.REGENERATING)
            questionnaire_path = project.metadata_.get("questionnaire_path")
            if not questionnaire_path:
                raise ValueError("Questionnaire path missing")
            questions = parse_questionnaire_pdf(questionnaire_path)
            store_questions(db, project, questions)
            set_project_status(db, project.id, ProjectStatus.READY)
        _set_status(request_uuid, RequestStatus.SUCCEEDED)
        logger.info("parse_questionnaire.success request=%s project=%s", request_id, project_id)
    except Exception as exc:  # pragma: no cover
        _set_status(request_uuid, RequestStatus.FAILED, detail=str(exc))
        logger.exception("parse_questionnaire.failed request=%s project=%s", request_id, project_id)
        raise


@celery_app.task(name="generate_all_answers")
def generate_all_answers_task(request_id: str, project_id: str) -> None:
    request_uuid = UUID(request_id)
    logger.info("generate_all_answers.start request=%s project=%s", request_id, project_id)
    _set_status(request_uuid, RequestStatus.RUNNING)
    try:
        with db_session() as db:
            set_project_status(db, UUID(project_id), ProjectStatus.REGENERATING)
            questions = get_questions_for_project(db, project_id)
            for question in questions:
                payload, status = generate_answer(question.prompt)
                upsert_ai_answer(db, question, payload, status)
            set_project_status(db, UUID(project_id), ProjectStatus.READY)
        _set_status(request_uuid, RequestStatus.SUCCEEDED)
        logger.info("generate_all_answers.success request=%s project=%s", request_id, project_id)
    except Exception as exc:  # pragma: no cover
        _set_status(request_uuid, RequestStatus.FAILED, detail=str(exc))
        logger.exception("generate_all_answers.failed request=%s project=%s", request_id, project_id)
        raise


@celery_app.task(name="generate_single_answer")
def generate_single_answer_task(request_id: str, project_id: str, question_id: str) -> None:
    request_uuid = UUID(request_id)
    logger.info("generate_single_answer.start request=%s project=%s question=%s", request_id, project_id, question_id)
    _set_status(request_uuid, RequestStatus.RUNNING)
    try:
        with db_session() as db:
            question = db.get(Question, UUID(question_id))
            if question is None:
                raise ValueError("Question not found")
            payload, status = generate_answer(question.prompt)
            upsert_ai_answer(db, question, payload, status)
        _set_status(request_uuid, RequestStatus.SUCCEEDED)
        logger.info(
            "generate_single_answer.success request=%s project=%s question=%s", request_id, project_id, question_id
        )
    except Exception as exc:  # pragma: no cover
        _set_status(request_uuid, RequestStatus.FAILED, detail=str(exc))
        logger.exception("generate_single_answer.failed request=%s project=%s question=%s", request_id, project_id, question_id)
        raise


@celery_app.task(name="evaluate_project")
def evaluate_project_task(request_id: str, project_id: str) -> None:
    request_uuid = UUID(request_id)
    logger.info("evaluate_project.start request=%s project=%s", request_id, project_id)
    _set_status(request_uuid, RequestStatus.RUNNING)
    try:
        with db_session() as db:
            evaluate_project(db, UUID(project_id))
        _set_status(request_uuid, RequestStatus.SUCCEEDED)
        logger.info("evaluate_project.success request=%s project=%s", request_id, project_id)
    except Exception as exc:  # pragma: no cover
        _set_status(request_uuid, RequestStatus.FAILED, detail=str(exc))
        logger.exception("evaluate_project.failed request=%s project=%s", request_id, project_id)
        raise


@celery_app.task(name="handle_config_change")
def handle_config_change_task(previous_signature: str | None, current_signature: str) -> None:
    logger.info(
        "config_change.start previous=%s current=%s",
        previous_signature,
        current_signature,
    )
    try:
        with db_session() as db:
            set_regen_inflight(db, True)
            projects = db.query(Project).all()
            documents = db.query(Document).all()
            for project in projects:
                set_project_status(db, project.id, ProjectStatus.REGENERATING)
            for document in documents:
                if document.path:
                    index_document(db, str(document.id))
            for project in projects:
                questionnaire_path = project.metadata_.get("questionnaire_path")
                if questionnaire_path:
                    questions = parse_questionnaire_pdf(questionnaire_path)
                    store_questions(db, project, questions)
            for project in projects:
                questions = get_questions_for_project(db, str(project.id))
                for question in questions:
                    payload, status = generate_answer(question.prompt)
                    upsert_ai_answer(db, question, payload, status)
                set_project_status(db, project.id, ProjectStatus.READY)
            set_regen_inflight(db, False)
        logger.info("config_change.success current=%s", current_signature)
    except Exception:  # pragma: no cover - task failure capture
        try:
            with db_session() as db:
                set_regen_inflight(db, False)
        except Exception:
            pass
        logger.exception("config_change.failed current=%s", current_signature)
        raise
