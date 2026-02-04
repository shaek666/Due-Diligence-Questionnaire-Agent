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
- Optional chat service: read-only Q&A against indexed corpus
- Review workflow: manual overrides and status changes
- Evaluation service: compares AI answers to human ground-truth

## Component Boundaries
- Frontend: React app for uploads, review, and evaluation UI.
- API service (FastAPI): orchestrates requests and serves data.
- Worker service: long-running jobs for indexing and generation.
- Storage:
  - Postgres: projects, documents, document_pages, questions, answers, requests, review_events, chat tables
  - Chroma: embeddings and chunk metadata
  - Object storage (local or filesystem): original files and parsed artifacts
  - Config state: pipeline signature for automatic regeneration

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
  - projects, documents, document_pages, questions, answers, requests, evaluation_runs
  - review_events (manual review audit trail)
  - chat_sessions, chat_messages
  - config_state (pipeline signature + regen state)
- Chroma collections:
  - coarse_retrieval (section-level)
  - citation_chunks (fine-grained, with page + bbox metadata; PDF uses word-level bbox via pdfplumber)
- File storage:
  - raw uploads
  - parsed text and layout metadata

## Status & Transitions
- Project status: CREATED -> INDEXING -> READY -> OUTDATED -> REGENERATING
- Answer status: GENERATED -> CONFIRMED | REJECTED | MANUAL_UPDATED | MISSING_DATA
- Request status: QUEUED -> RUNNING -> SUCCEEDED | FAILED

When a new document is indexed, ALL_DOCS projects must transition to OUTDATED.

## Configuration Change Regeneration
On startup, the API computes a pipeline signature (chunking, embeddings, and LLM
configuration). If it differs from the stored signature, a background task
re-indexes documents, re-parses questionnaires, and regenerates answers. A
lightweight watcher re-checks the signature at a fixed interval.

## Chat Extension
Chat uses the same retrieval pipeline as questionnaire answering and is strictly
read-only. It does not mutate project state or answers, and it shares the same
citations and confidence model for auditability.
