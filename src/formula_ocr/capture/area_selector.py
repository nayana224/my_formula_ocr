from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QWidget


class ScreenAreaSelector(QWidget):
    """현재 화면에서 사용자가 드래그한 영역을 선택한다."""

    captured = Signal(QPixmap)
    cancelled = Signal()

    def __init__(self) -> None:
        super().__init__()
        screen = QApplication.screenAt(self.cursor().pos()) or QApplication.primaryScreen()
        if screen is None:
            raise RuntimeError("사용 가능한 화면을 찾을 수 없습니다.")

        self._screen_geometry = screen.geometry()
        self._background = screen.grabWindow(0)
        self._start = QPoint()
        self._current = QPoint()
        self._dragging = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setGeometry(self._screen_geometry)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.activateWindow()
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self._background)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 110))

        selection = self._selection_rect()
        if selection.isEmpty():
            return

        source_rect = self._to_pixmap_rect(selection)
        painter.drawPixmap(selection, self._background, source_rect)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawRect(selection.adjusted(0, 0, -1, -1))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._start = event.position().toPoint()
        self._current = self._start
        self._dragging = True
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._dragging:
            return
        self._current = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or not self._dragging:
            return

        self._current = event.position().toPoint()
        self._dragging = False
        selection = self._selection_rect().intersected(self.rect())
        if selection.width() < 4 or selection.height() < 4:
            self.update()
            return

        source_rect = self._to_pixmap_rect(selection)
        cropped = self._background.copy(source_rect)
        self.hide()
        self.captured.emit(cropped)
        self.deleteLater()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            self.cancelled.emit()
            self.deleteLater()
            return
        super().keyPressEvent(event)

    def _selection_rect(self) -> QRect:
        if self._start.isNull() and self._current.isNull():
            return QRect()
        return QRect(self._start, self._current).normalized()

    def _to_pixmap_rect(self, widget_rect: QRect) -> QRect:
        if self.width() <= 0 or self.height() <= 0:
            return QRect()
        scale_x = self._background.width() / self.width()
        scale_y = self._background.height() / self.height()
        return QRect(
            round(widget_rect.x() * scale_x),
            round(widget_rect.y() * scale_y),
            round(widget_rect.width() * scale_x),
            round(widget_rect.height() * scale_y),
        )
