from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import Any
from uuid import UUID

import numpy as np
from difflib import SequenceMatcher
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.db_models import EvaluationRun, Project, Question


@lru_cache(maxsize=1)
def get_eval_model():
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(settings.embedding_model_name)
    except Exception:
        return None


def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    if vec_a.size == 0 or vec_b.size == 0:
        return 0.0
    denom = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    if denom == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)


def _fallback_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def evaluate_project(db: Session, project_id: UUID) -> EvaluationRun:
    project = db.get(Project, project_id)
    if project is None:
        raise ValueError("Project not found")
    model = get_eval_model()
    items: list[dict[str, Any]] = []
    scores: list[float] = []
    questions = db.query(Question).filter(Question.project_id == project.id).all()
    for question in questions:
        answer = question.answers[0] if question.answers else None
        ai_text = ""
        manual_text = ""
        if answer and answer.ai_answer:
            ai_text = answer.ai_answer.get("answer", "")
        if answer and answer.manual_answer:
            manual_text = answer.manual_answer.get("answer", "")
        if ai_text and manual_text:
            if model is None:
                score = _fallback_similarity(ai_text, manual_text)
            else:
                embeddings = model.encode([ai_text, manual_text])
                score = _cosine_similarity(embeddings[0], embeddings[1])
        else:
            score = 0.0
        scores.append(score)
        items.append(
            {
                "question_id": str(question.id),
                "score": score,
                "ai_answer": ai_text,
                "manual_answer": manual_text,
            }
        )
    summary = {
        "average_score": float(np.mean(scores)) if scores else 0.0,
        "question_count": len(items),
    }
    run = EvaluationRun(
        project_id=project.id,
        metrics=items,
        summary=summary,
        created_at=datetime.utcnow(),
    )
    db.add(run)
    db.flush()
    return run
