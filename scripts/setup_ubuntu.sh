#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Formula OCR은 ROS와 독립된 앱이므로 현재 shell의 ROS PYTHONPATH를 상속하지 않는다.
unset PYTHONPATH

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Rich Preview가 설치 후 네트워크 없이 동작하도록 공식 KaTeX asset을 준비한다.
python scripts/vendor_katex.py

# CPU-only 개발 환경에서 불필요한 CUDA runtime 설치를 피한다.
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[ocr,dev]"

echo
echo "설치 완료: ./scripts/run.sh"
echo "참고: pix2tex model checkpoint는 첫 OCR 실행 시 자동 다운로드될 수 있습니다."
