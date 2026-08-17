from __future__ import annotations

from PIL import Image
from PySide6.QtCore import QObject, Signal, Slot

from formula_ocr.ocr.pix2tex_engine import Pix2TexEngine


class OcrWorker(QObject):
    completed = Signal(str)
    failed = Signal(str)

    def __init__(self, engine: Pix2TexEngine) -> None:
        super().__init__()
        self._engine = engine

    @Slot(object)
    def recognize(self, image: Image.Image) -> None:
        try:
            latex = self._engine.recognize(image)
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.completed.emit(latex)
