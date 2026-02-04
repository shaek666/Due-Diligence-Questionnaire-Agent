# Runbook

This repository is Docker-only. The compose stack runs API, worker, database,
Redis, and frontend.

## A) Start
- `docker compose up --build`
- Frontend: http://localhost:5173
- API: http://localhost:8000

## A2) Optional GPU
- Install NVIDIA Container Toolkit on the host.
- `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build`
- Set `LLM_DEVICE=cuda` and `EMBEDDINGS_DEVICE=cuda` in `.env`.

## B) Rebuild Checklist
1) Pull latest code.
2) `docker compose build`
3) `docker compose up`
4) Confirm API: `http://localhost:8000/health`

## C) Migration Notes
- New tables: document_pages, review_events, config_state.
- The app uses `Base.metadata.create_all`, so missing tables are created on startup.
- If schema issues appear, reset volumes:
  - `docker compose down -v`
  - `docker compose up --build`

## D) Test Plan A-Z

A) Health
- GET /health returns {"status":"ok"}

B) Document ingestion
- Upload each file in `data/`
- Confirm /list-documents returns entries
- Confirm request status transitions to SUCCEEDED

C) Project creation
- Create project using questionnaire PDF
- Confirm project status READY after parsing
- Confirm questions appear in Project Detail

D) Generate answers
- Generate All Answers
- Confirm each answer has:
  - answerability_statement
  - answer
  - citations[]
  - confidence

E) Review workflow
- Update at least one answer to MANUAL_UPDATED
- Confirm new manual answer appears in Project Detail
- Confirm review events via /list-review-events

F) Evaluation
- Run evaluation
- Confirm /list-evaluations returns a new run
- Confirm summary includes qualitative assessment and keyword overlap metrics

G) OUTDATED logic
- Index a new document after project READY
- Confirm project status becomes OUTDATED

H) Request tracking
- Open Request Status screen and verify recent requests

I) Export
- From Evaluation Report screen, export CSV/Excel

J) Frontend sanity
- Ensure all tabs render without errors
- Validate navigation and state

K) Config change regeneration
- Change chunk sizes or model settings in `.env`
- Restart the stack
- Confirm regeneration requests appear in Request Status
