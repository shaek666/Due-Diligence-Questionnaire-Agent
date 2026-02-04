#!/usr/bin/env bash
set -euo pipefail

if command -v pkill >/dev/null 2>&1; then
  pkill -f "uvicorn app:app" || true
  pkill -f "celery -A src.workers.celery_app.celery_app" || true
  pkill -f "vite" || true
fi

redis-cli -p ${REDIS_PORT:-6380} shutdown || true
pg_ctl -D ${DATA_DIR:-/home/bubbleping/Makeball}/.pgdata stop || true

if [ -d "${DATA_DIR:-/home/bubbleping/Makeball}/.pgdata" ]; then
  rm -rf "${DATA_DIR:-/home/bubbleping/Makeball}/.pgdata"
fi
if [ -f "${DATA_DIR:-/home/bubbleping/Makeball}/.pglog" ]; then
  rm -f "${DATA_DIR:-/home/bubbleping/Makeball}/.pglog"
fi
