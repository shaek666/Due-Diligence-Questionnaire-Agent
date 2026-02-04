from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from sqlalchemy import func

from ..models.db_models import Project
from ..models.enums import ProjectStatus


def create_project(db: Session, name: str, scope: list[UUID], metadata: dict | None = None) -> Project:
    project = Project(
        name=name,
        scope=[str(item) for item in scope],
        status=ProjectStatus.CREATED,
        metadata_=metadata or {},
    )
    db.add(project)
    db.flush()
    return project


def update_project_scope(db: Session, project_id: UUID, scope: list[UUID]) -> Project | None:
    project = db.get(Project, project_id)
    if project is None:
        return None
    project.scope = [str(item) for item in scope]
    project.status = ProjectStatus.REGENERATING
    project.updated_at = datetime.utcnow()
    db.add(project)
    db.flush()
    return project


def mark_all_docs_outdated(db: Session) -> None:
    projects = db.query(Project).filter(func.json_array_length(Project.scope) == 0).all()
    for project in projects:
        project.status = ProjectStatus.OUTDATED
        project.updated_at = datetime.utcnow()
        db.add(project)


def set_project_status(db: Session, project_id: UUID, status: ProjectStatus) -> Project | None:
    project = db.get(Project, project_id)
    if project is None:
        return None
    project.status = status
    project.updated_at = datetime.utcnow()
    db.add(project)
    db.flush()
    return project


def list_projects(db: Session) -> list[Project]:
    return db.query(Project).order_by(Project.updated_at.desc()).all()
