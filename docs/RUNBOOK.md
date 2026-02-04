# Runbook

This runbook covers two modes:
- Real mode: real embeddings + real LLM (CPU)
- Fallback mode: fake embeddings + no LLM

## A. Real Mode (closer to production)

1) Create env
- ./scripts/setup_real_env.sh

2) Start backend services
- ./scripts/run_local_real.sh

3) Start frontend
- cd frontend
- npm install
- npm run dev

4) Open UI
- Frontend: http://localhost:5173
- API: http://localhost:8000

## B. Docker-Only Mode

- Run `docker compose up --build`
- Frontend: http://localhost:5173
- API: http://localhost:8000

## C. Test Plan A-Z

A) Health
- GET /health returns {"status":"ok"}

B) Document ingestion
- Upload each file in data/
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

F) Evaluation
- Run evaluation
- Confirm /list-evaluations returns a new run

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
