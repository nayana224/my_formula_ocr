from __future__ import annotations

from PIL import Image


class Pix2TexEngine:
    """pix2tex 모델의 로딩과 추론 경계를 관리한다."""

    def __init__(self) -> None:
        self._model = None

    def recognize(self, image: Image.Image) -> str:
        if self._model is None:
            self._model = self._load_model()
        result = self._model(image.convert("RGB"))
        return str(result).strip()

    @staticmethod
    def _load_model():
        try:
            from pix2tex.cli import LatexOCR
        except ImportError as exc:
            raise RuntimeError(
                'pix2tex가 설치되어 있지 않습니다. `pip install -e ".[ocr]"`로 설치하세요.'
            ) from exc
        return LatexOCR()
