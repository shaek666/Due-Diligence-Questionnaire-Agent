Backend Implementation (FastAPI + Celery)

Purpose
This folder holds the backend service implementation for the Questionnaire
Agent. It uses FastAPI, Celery, Postgres, and Chroma to support ingestion,
RAG answering, and evaluation.

Planned Modules
- src/api/        HTTP route handlers for the listed endpoints
- src/models/     Data models mirroring the spec data structures
- src/services/   Core business logic (project, answers, ingestion, evaluation)
- src/indexing/   Multi-layer indexing pipeline and chunking
- src/storage/    Persistence layer (DB, vector store, object storage)
- src/workers/    Async/background processing and request status tracking
- src/utils/      Shared helpers, validation, and constants

Endpoints (implemented)
- POST /create-project-async
- POST /generate-single-answer
- POST /generate-all-answers
- POST /update-project-async
- POST /update-answer
- POST /evaluate-project-async
- GET /get-project-info
- GET /get-project-status
- GET /list-projects
- POST /index-document-async
- GET /list-documents
- GET /get-request-status
- GET /list-requests
- GET /get-evaluation
- GET /list-evaluations

Run (Docker)
- From repo root: docker compose up --build
- API: http://localhost:8000

Run (Local)
- pip install -r requirements.txt
- uvicorn app:app --reload

CPU Notes
- Default model is Mistral-7B. On CPU it may be slow; you can set a smaller model via LLM_MODEL_NAME.
- To run without downloading models (offline), set LLM_LOCAL_FILES_ONLY=true.
- To force extractive fallback without an LLM, set LLM_BACKEND=none.

Embedding Notes
- Default: EMBEDDINGS_BACKEND=sentence_transformers
- Low-resource fallback: EMBEDDINGS_BACKEND=fake

Local Scripts
- scripts/setup_real_env.sh: creates a Python 3.11 env with CPU-only torch.
- scripts/run_local_real.sh: starts Postgres/Redis + API/worker with real embeddings + LLM.
- scripts/run_local_fallback.sh: starts Postgres/Redis + API/worker with fake embeddings + no LLM.
- scripts/stop_local.sh: stops services and cleans local PG data.
