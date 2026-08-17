from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = REPO_ROOT / "dist" / "FormulaOCR"
RELEASE_DIR = REPO_ROOT / "release"


def main() -> int:
    parser = argparse.ArgumentParser(description="Formula OCR standalone ZIP 생성")
    parser.add_argument("--platform", required=True, choices=("Ubuntu", "Windows"))
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    if not DIST_DIR.is_dir():
        raise RuntimeError(f"PyInstaller 출력 폴더가 없습니다: {DIST_DIR}")

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    archive_base = RELEASE_DIR / f"FormulaOCR-{args.version}-{args.platform}"
    archive_path = Path(
        shutil.make_archive(
            str(archive_base),
            "zip",
            root_dir=DIST_DIR.parent,
            base_dir=DIST_DIR.name,
        )
    )
    print(f"Release archive ready: {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
