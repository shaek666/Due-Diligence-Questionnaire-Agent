# Architecture Design — Questionnaire Agent

## System Overview
The system ingests reference documents and a questionnaire, indexes the
documents, parses the questionnaire into structured questions, then generates
answers with citations and confidence scores. It supports human review and
evaluation against ground-truth answers.

Core components:
- Ingestion service: uploads and normalizes documents
- Indexing service: chunks, embeds, and stores citation metadata
- Questionnaire parser: extracts sections and questions
- Answering service: retrieval + generation + citations + confidence
- Review workflow: manual overrides and status changes
- Evaluation service: compares AI answers to human ground-truth

## Component Boundaries
- Frontend: React app for uploads, review, and evaluation UI.
- API service (FastAPI): orchestrates requests and serves data.
- Worker service: long-running jobs for indexing and generation.
- Storage:
  - Postgres: projects, questions, answers, requests, reviews
  - Chroma: embeddings and chunk metadata
  - Object storage (local or filesystem): original files and parsed artifacts

## Data Flow (Happy Path)
1) Upload reference documents.
2) Index documents (async).
3) Upload questionnaire PDF and parse into sections/questions.
4) Create project with scope (ALL_DOCS or a subset).
5) Generate answers with citations and confidence (async).
6) Review answers; update status and manual overrides.
7) Evaluate against ground-truth (optional).

## Storage Layout
- Postgres tables:
  - projects, documents, document_pages, questions, answers, requests,
    evaluations, review_events
- Chroma collections:
  - coarse_retrieval (section-level)
  - citation_chunks (fine-grained, with page + bbox metadata)
- File storage:
  - raw uploads
  - parsed text and layout metadata

## Status & Transitions
- Project status: CREATED -> INDEXING -> READY -> OUTDATED -> REGENERATING
- Answer status: GENERATED -> CONFIRMED | REJECTED | MANUAL_UPDATED | MISSING_DATA
- Request status: QUEUED -> RUNNING -> SUCCEEDED | FAILED

When a new document is indexed, ALL_DOCS projects must transition to OUTDATED.
