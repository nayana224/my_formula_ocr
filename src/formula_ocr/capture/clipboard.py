from __future__ import annotations

from io import BytesIO

from PIL import Image
from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtGui import QImage


def qimage_to_pil(image: QImage) -> Image.Image:
    """Qt image를 OCR 입력용 PIL image로 변환한다."""
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not image.save(buffer, "PNG"):
        raise RuntimeError("Clipboard image를 PNG로 변환하지 못했습니다.")
    return Image.open(BytesIO(bytes(buffer.data()))).copy()
