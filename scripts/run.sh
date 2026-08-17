#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -d .venv ]]; then
  echo "[ERROR] .venv가 없습니다. 먼저 ./scripts/setup_ubuntu.sh 를 실행하세요." >&2
  exit 1
fi

source .venv/bin/activate
exec python -m formula_ocr
