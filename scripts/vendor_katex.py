from __future__ import annotations

import hashlib
import io
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path


KATEX_VERSION = "0.17.0"
KATEX_ARCHIVE_URL = (
    f"https://github.com/KaTeX/KaTeX/releases/download/v{KATEX_VERSION}/katex.zip"
)
KATEX_ARCHIVE_SHA256 = "8199fe2230362f2933fbaa26d34a18cdf491a9c8c6822c07e46cb4f00028fded"

REPO_ROOT = Path(__file__).resolve().parents[1]
DESTINATION = REPO_ROOT / "src" / "formula_ocr" / "assets" / "katex"

_REQUIRED_FILES = (
    "katex.min.css",
    "katex.min.js",
)


def main() -> int:
    if _assets_ready():
        print(f"KaTeX {KATEX_VERSION} assets already available: {DESTINATION}")
        return 0

    print(f"Downloading KaTeX {KATEX_VERSION} release assets...")
    archive = _download_archive()
    _verify_archive(archive)
    _extract_assets(archive)

    if not _assets_ready():
        raise RuntimeError("KaTeX asset 설치가 완료되지 않았습니다.")

    print(f"KaTeX {KATEX_VERSION} offline assets ready: {DESTINATION}")
    return 0


def _assets_ready() -> bool:
    if not all((DESTINATION / name).is_file() for name in _REQUIRED_FILES):
        return False
    fonts_dir = DESTINATION / "fonts"
    return fonts_dir.is_dir() and any(fonts_dir.glob("*.woff2"))


def _download_archive() -> bytes:
    request = urllib.request.Request(
        KATEX_ARCHIVE_URL,
        headers={"User-Agent": "Formula-OCR-KaTeX-Vendor"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def _verify_archive(archive: bytes) -> None:
    digest = hashlib.sha256(archive).hexdigest()
    if digest != KATEX_ARCHIVE_SHA256:
        raise RuntimeError(
            "KaTeX archive SHA-256 불일치: "
            f"expected={KATEX_ARCHIVE_SHA256}, actual={digest}"
        )


def _extract_assets(archive: bytes) -> None:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    fonts_destination = DESTINATION / "fonts"

    with tempfile.TemporaryDirectory(prefix="formula-ocr-katex-") as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
            zipped.extractall(temp_path)

        release_root = temp_path / "katex"
        for name in _REQUIRED_FILES:
            shutil.copy2(release_root / name, DESTINATION / name)

        source_fonts = release_root / "fonts"
        fonts_destination.mkdir(parents=True, exist_ok=True)
        for font in source_fonts.glob("*.woff2"):
            shutil.copy2(font, fonts_destination / font.name)


if __name__ == "__main__":
    raise SystemExit(main())
