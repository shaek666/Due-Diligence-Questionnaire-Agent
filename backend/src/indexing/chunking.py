from __future__ import annotations

import json
import re
import uuid
from typing import Iterable, Tuple

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..services.ingestion import PageText, WordBox


def chunk_pages(
    document_id: str,
    source_name: str,
    pages: Iterable[PageText],
    chunk_size: int,
    chunk_overlap: int,
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks: list[Document] = []
    for page in pages:
        page_norm, word_spans = _build_word_spans(page.words)
        search_start = 0
        texts = splitter.split_text(page.text)
        bbox = None
        for index, text in enumerate(texts, start=1):
            bbox = _compute_chunk_bbox(text, page_norm, word_spans, search_start)
            if bbox:
                search_start = bbox.pop("_next_search_start")
                if page.page_width and page.page_height:
                    bbox["page_width"] = float(page.page_width)
                    bbox["page_height"] = float(page.page_height)
            metadata = {
                "document_id": document_id,
                "source_name": source_name,
                "page_number": page.page_number,
                "chunk_id": f"{document_id}-{page.page_number}-{index}-{uuid.uuid4().hex}",
            }
            if bbox:
                metadata["bounding_box_json"] = json.dumps(bbox)
            chunks.append(
                Document(
                    page_content=text,
                    metadata=metadata,
                )
            )
    return chunks


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _build_word_spans(words: list[WordBox]) -> tuple[str, list[tuple[int, int, WordBox]]]:
    tokens: list[str] = []
    spans: list[tuple[int, int, WordBox]] = []
    cursor = 0
    for word in words:
        token = _normalize_text(word.text)
        if not token:
            continue
        if tokens:
            cursor += 1
        start = cursor
        end = start + len(token)
        tokens.append(token)
        spans.append((start, end, word))
        cursor = end
    return " ".join(tokens), spans


def _compute_chunk_bbox(
    chunk_text: str,
    page_norm: str,
    word_spans: list[tuple[int, int, WordBox]],
    search_start: int,
) -> dict | None:
    if not page_norm or not word_spans:
        return None
    chunk_norm = _normalize_text(chunk_text)
    if not chunk_norm:
        return None
    index = page_norm.find(chunk_norm, search_start)
    if index == -1:
        index = page_norm.find(chunk_norm)
    if index == -1:
        return None
    start = index
    end = start + len(chunk_norm)
    selected: list[WordBox] = []
    for span_start, span_end, word in word_spans:
        if span_end < start or span_start > end:
            continue
        selected.append(word)
    if not selected:
        return None
    x0 = min(word.x0 for word in selected)
    y0 = min(word.y0 for word in selected)
    x1 = max(word.x1 for word in selected)
    y1 = max(word.y1 for word in selected)
    return {
        "x0": float(x0),
        "y0": float(y0),
        "x1": float(x1),
        "y1": float(y1),
        "unit": "pt",
        "source": "pdfplumber",
        "_next_search_start": end,
    }
