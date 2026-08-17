#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# CPU-only 개발 환경에서 불필요한 CUDA runtime 설치를 피한다.
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[ocr,dev]"

echo
echo "설치 완료: ./scripts/run.sh"
echo "참고: pix2tex model checkpoint는 첫 OCR 실행 시 자동 다운로드될 수 있습니다."
