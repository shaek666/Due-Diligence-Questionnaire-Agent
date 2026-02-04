from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.db_models import Project, Question
from ..services.questionnaire import ParsedQuestion


def store_questions(db: Session, project: Project, questions: list[ParsedQuestion]) -> None:
    db.query(Question).filter(Question.project_id == project.id).delete()
    for question in questions:
        db.add(
            Question(
                project_id=project.id,
                section_title=question.section_title,
                order=question.order,
                prompt=question.prompt,
            )
        )
    db.flush()


def get_questions_for_project(db: Session, project_id: str) -> list[Question]:
    from uuid import UUID

    project_uuid = UUID(project_id)
    return (
        db.query(Question)
        .filter(Question.project_id == project_uuid)
        .order_by(Question.order.asc())
        .all()
    )
