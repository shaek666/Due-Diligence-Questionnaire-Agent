#!/usr/bin/env bash
set -euo pipefail

PG_PORT=${PG_PORT:-5433}
REDIS_PORT=${REDIS_PORT:-6380}
DATA_DIR=${DATA_DIR:-/home/bubbleping/Makeball}
BACKEND_DIR=${BACKEND_DIR:-$DATA_DIR/backend}

# Start Postgres
if [ ! -d "$DATA_DIR/.pgdata" ]; then
  initdb -D "$DATA_DIR/.pgdata"
fi
pg_ctl -D "$DATA_DIR/.pgdata" -o "-p $PG_PORT" -l "$DATA_DIR/.pglog" start
createdb -p "$PG_PORT" makeball || true

# Start Redis
redis-server --port "$REDIS_PORT" --daemonize yes

export ENVIRONMENT=local
export DATABASE_URL=postgresql+psycopg://$USER@localhost:$PG_PORT/makeball
export WORKER_BROKER_URL=redis://localhost:$REDIS_PORT/0
export WORKER_RESULT_BACKEND=redis://localhost:$REDIS_PORT/1
export STORAGE_PATH=$DATA_DIR/storage
export CHROMA_PATH=$DATA_DIR/storage/chroma
export EMBEDDINGS_BACKEND=fake
export LLM_BACKEND=none

mkdir -p "$DATA_DIR/storage"

PYTHONPATH="$BACKEND_DIR" uvicorn app:app --host 0.0.0.0 --port 8000 --app-dir "$BACKEND_DIR" &
API_PID=$!

PYTHONPATH="$BACKEND_DIR" celery -A src.workers.celery_app.celery_app worker --loglevel=info &
WORKER_PID=$!

echo "API PID: $API_PID"
echo "Worker PID: $WORKER_PID"

echo "Frontend: cd frontend && npm install && npm run dev"
