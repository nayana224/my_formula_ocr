from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QResizeEvent
from PySide6.QtWidgets import QLabel


class ImageView(QLabel):
    image_file_dropped = Signal(object)

    def __init__(self) -> None:
        super().__init__("이미지를 열거나 여기에 드래그하세요.\nCtrl+V로 clipboard 이미지도 붙여넣을 수 있습니다.")
        self._pixmap = QPixmap()
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(420, 300)
        self.setStyleSheet(
            "QLabel { border: 2px dashed #777; border-radius: 10px; padding: 16px; }"
        )

    def set_image(self, pixmap: QPixmap) -> None:
        self._pixmap = pixmap
        self._refresh_scaled_pixmap()

    def clear_image(self) -> None:
        self._pixmap = QPixmap()
        self.clear()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        urls = event.mimeData().urls()
        if len(urls) == 1 and _is_supported_image(Path(urls[0].toLocalFile())):
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        path = Path(event.mimeData().urls()[0].toLocalFile())
        self.image_file_dropped.emit(path)
        event.acceptProposedAction()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._refresh_scaled_pixmap()

    def _refresh_scaled_pixmap(self) -> None:
        if self._pixmap.isNull():
            return
        available = self.contentsRect().size()
        scaled = self._pixmap.scaled(
            available,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)


def _is_supported_image(path: Path) -> bool:
    return path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
