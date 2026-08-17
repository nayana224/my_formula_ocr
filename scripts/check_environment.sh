#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -x .venv/bin/python ]]; then
  echo "[FAIL] .venv가 없습니다. ./scripts/setup_ubuntu.sh 를 먼저 실행하세요."
  exit 1
fi

source .venv/bin/activate
python - <<'PY'
import importlib
import platform
import sys

print(f"Python: {sys.version.split()[0]}")
print(f"Platform: {platform.platform()}")

required = ("PySide6", "PIL", "matplotlib", "torch", "pix2tex")
failed = False
for module_name in required:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        failed = True
        print(f"[FAIL] {module_name}: {exc}")
    else:
        version = getattr(module, "__version__", "installed")
        print(f"[OK] {module_name}: {version}")

if failed:
    raise SystemExit(1)
PY
