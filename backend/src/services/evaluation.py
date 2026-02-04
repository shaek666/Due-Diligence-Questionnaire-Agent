from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import Any
from uuid import UUID

import numpy as np
from difflib import SequenceMatcher
import re
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


_STOPWORDS = {
    "the",
    "and",
    "for",
    "are",
    "with",
    "that",
    "this",
    "from",
    "have",
    "has",
    "was",
    "were",
    "will",
    "shall",
    "may",
    "your",
    "you",
    "our",
    "their",
    "they",
    "them",
    "not",
    "but",
    "into",
    "over",
    "under",
    "between",
    "within",
}


def _keyword_tokens(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {token for token in tokens if len(token) > 2 and token not in _STOPWORDS}


def _keyword_overlap(a: str, b: str) -> float:
    a_tokens = _keyword_tokens(a)
    b_tokens = _keyword_tokens(b)
    if not a_tokens or not b_tokens:
        return 0.0
    intersection = a_tokens & b_tokens
    union = a_tokens | b_tokens
    return len(intersection) / len(union)


def _qualitative_assessment(score: float) -> str:
    if score >= 0.8:
        return "Strong alignment between AI and human answers."
    if score >= 0.6:
        return "Moderate alignment with some gaps."
    if score >= 0.4:
        return "Weak alignment; review required."
    return "Low alignment; significant differences detected."


def evaluate_project(db: Session, project_id: UUID) -> EvaluationRun:
    project = db.get(Project, project_id)
    if project is None:
        raise ValueError("Project not found")
    model = get_eval_model()
    items: list[dict[str, Any]] = []
    combined_scores: list[float] = []
    semantic_scores: list[float] = []
    keyword_scores: list[float] = []
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
                semantic_score = _fallback_similarity(ai_text, manual_text)
            else:
                embeddings = model.encode([ai_text, manual_text])
                semantic_score = _cosine_similarity(embeddings[0], embeddings[1])
            keyword_score = _keyword_overlap(ai_text, manual_text)
        else:
            semantic_score = 0.0
            keyword_score = 0.0
        combined_score = (semantic_score * 0.7) + (keyword_score * 0.3)
        combined_scores.append(combined_score)
        semantic_scores.append(semantic_score)
        keyword_scores.append(keyword_score)
        items.append(
            {
                "question_id": str(question.id),
                "score": combined_score,
                "semantic_score": semantic_score,
                "keyword_overlap": keyword_score,
                "ai_answer": ai_text,
                "manual_answer": manual_text,
            }
        )
    summary = {
        "average_score": float(np.mean(combined_scores)) if combined_scores else 0.0,
        "average_semantic_score": float(np.mean(semantic_scores)) if semantic_scores else 0.0,
        "average_keyword_overlap": float(np.mean(keyword_scores)) if keyword_scores else 0.0,
        "question_count": len(items),
        "qualitative_assessment": _qualitative_assessment(
            float(np.mean(combined_scores)) if combined_scores else 0.0
        ),
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
