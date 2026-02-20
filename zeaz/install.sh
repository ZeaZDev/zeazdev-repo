#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PROFILE_PATH="${ROOT_DIR}/profiles/prod.env"

python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip
pip install -r "${ROOT_DIR}/requirements.txt"

if [[ -f "${PROFILE_PATH}" ]]; then
  set -a
  source "${PROFILE_PATH}"
  set +a
fi

python -m app.migrate

echo "Install complete. Start API with:"
echo "  ${VENV_DIR}/bin/gunicorn -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8000"
