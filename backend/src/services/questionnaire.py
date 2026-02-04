from __future__ import annotations

import re
from dataclasses import dataclass

from .ingestion import PageText, parse_pdf


@dataclass
class ParsedQuestion:
    section_title: str
    order: int
    prompt: str


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_questionnaire_pdf(path: str) -> list[ParsedQuestion]:
    pages = parse_pdf(path)
    questions: list[ParsedQuestion] = []
    current_section = "General"
    order = 1
    question_pattern = re.compile(r"^\d+(\.\d+)*")
    for page in pages:
        lines = [line.strip() for line in page.text.splitlines() if line.strip()]
        for line in lines:
            if line.isupper() and len(line) > 5:
                current_section = line.title()
                continue
            if line.endswith("?") or question_pattern.match(line) or line.lower().startswith("please "):
                questions.append(
                    ParsedQuestion(section_title=current_section, order=order, prompt=_normalize_text(line))
                )
                order += 1
    return questions
