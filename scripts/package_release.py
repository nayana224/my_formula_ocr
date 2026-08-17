from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = REPO_ROOT / "dist" / "FormulaOCR"
WINDOWS_EXE = REPO_ROOT / "dist" / "FormulaOCR.exe"
RELEASE_DIR = REPO_ROOT / "release"


def main() -> int:
    parser = argparse.ArgumentParser(description="Formula OCR standalone ZIP 생성")
    parser.add_argument("--platform", required=True, choices=("Ubuntu", "Windows"))
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = RELEASE_DIR / f"FormulaOCR-{args.version}-{args.platform}.zip"

    if args.platform == "Windows":
        _package_windows(archive_path)
    else:
        _package_ubuntu(archive_path)

    print(f"Release archive ready: {archive_path}")
    return 0


def _package_windows(archive_path: Path) -> None:
    if not WINDOWS_EXE.is_file():
        raise RuntimeError(f"PyInstaller 실행 파일이 없습니다: {WINDOWS_EXE}")

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(WINDOWS_EXE, arcname="FormulaOCR.exe")


def _package_ubuntu(archive_path: Path) -> None:
    if not DIST_DIR.is_dir():
        raise RuntimeError(f"PyInstaller 출력 폴더가 없습니다: {DIST_DIR}")

    archive_base = archive_path.with_suffix("")
    generated = Path(
        shutil.make_archive(
            str(archive_base),
            "zip",
            root_dir=DIST_DIR.parent,
            base_dir=DIST_DIR.name,
        )
    )
    if generated != archive_path:
        raise RuntimeError(f"예상하지 못한 archive 경로입니다: {generated}")


if __name__ == "__main__":
    raise SystemExit(main())
