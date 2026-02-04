from __future__ import annotations

from datetime import datetime
from typing import List, Tuple
from uuid import UUID

from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from sqlalchemy.orm import Session

from ..models.db_models import Answer, Question
from ..models.enums import AnswerStatus
from ..models.schemas import AnswerPayload, Citation
from ..services.llm import get_llm
from ..services.retrieval import retrieve_citations


ANSWER_PROMPT = PromptTemplate(
    input_variables=["question", "context"],
    template=(
        "You are a due diligence assistant. Answer the question using ONLY the context. "
        "If the context does not contain the answer, say you do not have enough information.\n\n"
        "Question: {question}\n\n"
        "Context:\n{context}\n\n"
        "Answer:"
    ),
)


def _build_citations(docs: List[Tuple[Document, float]]) -> list[Citation]:
    citations: list[Citation] = []
    for doc, score in docs:
        meta = doc.metadata or {}
        snippet = doc.page_content[:280]
        document_id = meta.get("document_id")
        if not document_id:
            continue
        citations.append(
            Citation(
                document_id=UUID(document_id),
                page_number=int(meta.get("page_number", 0)),
                chunk_id=str(meta.get("chunk_id")),
                snippet=snippet,
                score=float(score),
            )
        )
    return citations


def _confidence_from_scores(scores: list[float]) -> float:
    if not scores:
        return 0.1
    normalized = [1.0 / (1.0 + score) for score in scores]
    base = sum(normalized) / len(normalized)
    return max(0.05, min(0.95, base))


def generate_answer(question_text: str) -> tuple[AnswerPayload, AnswerStatus]:
    docs = retrieve_citations(question_text)
    if not docs:
        payload = AnswerPayload(
            answer="No relevant information found in the indexed documents.",
            answerable=False,
            answerability_statement="Not answerable based on available documents.",
            confidence=0.1,
            citations=[],
        )
        return payload, AnswerStatus.MISSING_DATA
    context = "\n\n".join([doc.page_content for doc, _ in docs])
    llm = get_llm()
    if llm is None:
        response = f"Extractive fallback response:\n{context[:800]}".strip()
        answerability_statement = "Answer generated from retrieved context without a loaded LLM."
    else:
        prompt = ANSWER_PROMPT.format(question=question_text, context=context)
        try:
            response = llm.invoke(prompt)
        except AttributeError:
            response = llm(prompt)
        response = str(response).strip()
        answerability_statement = "Answerable based on retrieved documents."
    scores = [score for _, score in docs]
    payload = AnswerPayload(
        answer=response,
        answerable=True,
        answerability_statement=answerability_statement,
        confidence=_confidence_from_scores(scores),
        citations=_build_citations(docs),
    )
    return payload, AnswerStatus.GENERATED


def upsert_ai_answer(db: Session, question: Question, payload: AnswerPayload, status: AnswerStatus) -> Answer:
    answer = db.query(Answer).filter(Answer.question_id == question.id).first()
    if answer is None:
        answer = Answer(question_id=question.id)
    answer.ai_answer = payload.model_dump(mode="json")
    answer.status = status
    answer.updated_at = datetime.utcnow()
    db.add(answer)
    db.flush()
    return answer


def update_manual_answer(
    db: Session, answer_id: UUID, status: AnswerStatus, manual_answer: AnswerPayload | None
) -> Answer | None:
    answer = db.get(Answer, answer_id)
    if answer is None:
        return None
    answer.status = status
    if manual_answer is not None:
        answer.manual_answer = manual_answer.model_dump(mode="json")
    answer.updated_at = datetime.utcnow()
    db.add(answer)
    db.flush()
    return answer
