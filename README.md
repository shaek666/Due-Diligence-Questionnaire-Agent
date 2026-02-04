# Due Diligence Questionnaire Agent

A full-stack AI system to automate due diligence questionnaires. It indexes company documents, parses questionnaire files into structured questions, generates answers with citations and confidence scores, and supports human review plus evaluation against ground-truth answers.
Optional chat is included for read-only Q&A against the same indexed corpus.

See `backend/README.md` and `frontend/README.md` for service-specific details.

## Required Documentation
- Architecture Design: system overview, component boundaries, data flow, storage.
- Functional Design: user flows, API behaviors, status transitions, edge cases.
- Testing & Evaluation: dataset testing plan, QA checklist, evaluation metrics.

## Dataset Testing
- Sample PDFs live in `data/` and are intended for ingestion and QA smoke tests.
- Use `data/ILPA_Due_Diligence_Questionnaire_v1.2.pdf` as the questionnaire input and the other PDFs as reference documents for answering.
- Index the reference PDFs, create a project scoped to ALL_DOCS, and generate answers to validate citations and confidence outputs.
- Add a new document after indexing to confirm the ALL_DOCS project transitions to OUTDATED as described in the spec.

## Quick Start (Docker)
- `docker compose up --build`
- API: http://localhost:8000
- Frontend: http://localhost:5173

## Docker Rebuild Checklist
1) Pull latest code.
2) Rebuild images: `docker compose build`
3) Start services: `docker compose up`
4) Confirm API is healthy: `http://localhost:8000/health`

## Migration Notes
- New tables were added (document_pages, review_events, chat tables, config_state).
- The app uses `Base.metadata.create_all`, so missing tables are created automatically on startup.
- If you encounter schema issues from an older run, remove the DB volume and restart:
  - `docker compose down -v`
  - `docker compose up --build`

## Quick Start (Local)
Local scripts have been removed. Use Docker Compose.

## QA Checklist
- Upload sample PDFs in `data/` via Document Management.
- Create a project with the questionnaire PDF and scope [] for ALL_DOCS.
- Wait for parsing and index tasks to complete (check Request Status screen).
- Generate all answers and review citations and confidence.
- Run evaluation after adding manual answers for a subset of questions.

## Runbook
- See `docs/RUNBOOK.md` for full run modes and the A-Z test plan.
