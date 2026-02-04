from __future__ import annotations

import uuid
from typing import Iterable

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..services.ingestion import PageText


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
        texts = splitter.split_text(page.text)
        bbox = None
        if page.page_width and page.page_height:
            bbox = {
                "x0": 0.0,
                "y0": 0.0,
                "x1": float(page.page_width),
                "y1": float(page.page_height),
                "unit": "pt",
                "source": "page",
            }
        for index, text in enumerate(texts, start=1):
            metadata = {
                "document_id": document_id,
                "source_name": source_name,
                "page_number": page.page_number,
                "chunk_id": f"{document_id}-{page.page_number}-{index}-{uuid.uuid4().hex}",
            }
            if bbox:
                metadata["bounding_box"] = bbox
            chunks.append(
                Document(
                    page_content=text,
                    metadata=metadata,
                )
            )
    return chunks
