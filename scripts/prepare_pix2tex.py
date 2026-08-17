from __future__ import annotations

from pathlib import Path


def main() -> int:
    """Standalone 빌드 전에 pix2tex 체크포인트를 다운로드하고 검증한다."""
    import pix2tex
    from pix2tex.cli import LatexOCR

    package_dir = Path(pix2tex.__file__).resolve().parent
    checkpoint_dir = package_dir / "model" / "checkpoints"
    weights_path = checkpoint_dir / "weights.pth"

    if not weights_path.is_file():
        print("Preparing pix2tex model checkpoints...")
        LatexOCR()

    if not weights_path.is_file():
        raise RuntimeError(f"pix2tex weights가 준비되지 않았습니다: {weights_path}")

    print(f"pix2tex weights ready: {weights_path}")
    resizer_path = checkpoint_dir / "image_resizer.pth"
    if resizer_path.is_file():
        print(f"pix2tex image resizer ready: {resizer_path}")
    else:
        print("pix2tex image resizer는 없습니다. 기본 OCR 모델만 포함합니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
