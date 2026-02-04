#!/usr/bin/env bash
set -euo pipefail

ENV_NAME=${ENV_NAME:-makeball-real}
PYTHON_VERSION=${PYTHON_VERSION:-3.11}

conda create -y -n "$ENV_NAME" python="$PYTHON_VERSION"

conda run -n "$ENV_NAME" pip install --upgrade pip
conda run -n "$ENV_NAME" pip install -r backend/requirements-base.txt

# CPU-only torch from PyTorch index
conda run -n "$ENV_NAME" pip install --index-url https://download.pytorch.org/whl/cpu torch==2.2.2
conda run -n "$ENV_NAME" pip install transformers sentence-transformers

echo "Environment $ENV_NAME ready."
