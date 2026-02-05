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
    question_pattern = re.compile(r"^(?P<num>\d+(?:\.\d+)*)(?:\)|\.|\s)\s*(?P<text>.+)?$")
    header_stopwords = {
        "ilpa",
        "due diligence questionnaire",
        "ilpa due diligence questionnaire",
        "private equity",
        "infrastructure",
    }
    action_starters = ("please", "describe", "provide", "explain", "list", "state", "confirm", "identify")

    def is_header(line: str) -> bool:
        collapsed = line.lower()
        if collapsed in header_stopwords:
            return True
        if collapsed.startswith("page ") and collapsed[5:].isdigit():
            return True
        if collapsed.isdigit():
            return True
        return False

    def looks_like_address(line: str) -> bool:
        if not re.search(r"\d", line):
            return False
        address_terms = r"\b(st|street|ave|avenue|rd|road|suite|ste|blvd|drive|dr|lane|ln|nw|ne|se|sw)\b"
        if re.search(address_terms, line, re.IGNORECASE):
            return True
        if re.search(r"\b\d{5}(?:-\d{4})?\b", line):
            return True
        return False

    def flush(buffer: list[str]) -> None:
        nonlocal order
        if not buffer:
            return
        merged = _normalize_text(" ".join(buffer))
        if merged:
            questions.append(ParsedQuestion(section_title=current_section, order=order, prompt=merged))
            order += 1

    buffer: list[str] = []
    for page in pages:
        lines = [line.strip() for line in page.text.splitlines() if line.strip()]
        for raw_line in lines:
            line = _normalize_text(raw_line)
            if not line or is_header(line):
                continue
            line = re.sub(r"(\d)\.\s+(\d)", r"\1.\2", line)
            if line.isupper() and len(line) > 5:
                flush(buffer)
                buffer = []
                current_section = line.title()
                continue
            match = question_pattern.match(line)
            if match:
                candidate = (match.group("text") or "").strip()
                if candidate and looks_like_address(candidate) and not candidate.lower().startswith(action_starters):
                    continue
                flush(buffer)
                buffer = []
                question_text = candidate or ""
                prefix = match.group("num")
                if question_text:
                    buffer.append(f"{prefix}. {question_text}")
                else:
                    buffer.append(f"{prefix}.")
                continue
            if buffer:
                buffer.append(line)
            elif line.lower().startswith(action_starters) or line.endswith("?"):
                buffer = [line]
    flush(buffer)
    return questions
