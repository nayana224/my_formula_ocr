from __future__ import annotations

from pathlib import Path

from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6.QtCore import QStandardPaths, Qt, QThread, Signal
from PySide6.QtGui import QAction, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from formula_ocr.capture.clipboard import qimage_to_pil
from formula_ocr.history.database import HistoryDatabase
from formula_ocr.latex.formatter import CopyFormat, format_latex
from formula_ocr.latex.renderer import render_latex_preview
from formula_ocr.ocr.pix2tex_engine import Pix2TexEngine
from formula_ocr.ui.image_view import ImageView
from formula_ocr.ui.ocr_worker import OcrWorker


class MainWindow(QMainWindow):
    recognize_requested = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._image: Image.Image | None = None
        self._ocr_busy = False
        self._engine = Pix2TexEngine()
        self._history = HistoryDatabase(_history_path())
        self._worker_thread = QThread(self)
        self._worker = OcrWorker(self._engine)
        self._worker.moveToThread(self._worker_thread)
        self.recognize_requested.connect(self._worker.recognize)
        self._worker.completed.connect(self._on_ocr_completed)
        self._worker.failed.connect(self._on_ocr_failed)
        self._worker_thread.start()

        self.setWindowTitle("Formula OCR")
        self.resize(1180, 760)
        self.setStatusBar(QStatusBar(self))
        self._build_ui()
        self._build_actions()
        self._reload_history()

    def closeEvent(self, event) -> None:
        if self._ocr_busy:
            QMessageBox.information(
                self,
                "OCR running",
                "OCR 실행 중에는 안전하게 종료할 수 없습니다. 완료 후 다시 종료해주세요.",
            )
            event.ignore()
            return
        self._worker_thread.quit()
        self._worker_thread.wait()
        super().closeEvent(event)

    def _build_ui(self) -> None:
        self.image_view = ImageView()
        self.image_view.image_file_dropped.connect(self.load_image_file)

        self.latex_edit = QPlainTextEdit()
        self.latex_edit.setPlaceholderText("OCR 결과가 여기에 표시됩니다.")
        self.latex_edit.textChanged.connect(self._refresh_preview)

        self.preview = QLabel("LaTeX preview")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(180)
        self.preview.setStyleSheet("QLabel { border: 1px solid #555; border-radius: 8px; }")

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("LaTeX"))
        right_layout.addWidget(self.latex_edit, 2)
        right_layout.addWidget(QLabel("Preview (mathtext subset)"))
        right_layout.addWidget(self.preview, 1)
        right_panel = QWidget()
        right_panel.setLayout(right_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.image_view)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        button_layout = QHBoxLayout()
        buttons = (
            ("Open", self.open_image_dialog),
            ("Paste Image", self.paste_image),
            ("Run OCR", self.run_ocr),
            ("Copy LaTeX", lambda: self.copy_latex(CopyFormat.LATEX)),
            ("Copy $...$", lambda: self.copy_latex(CopyFormat.INLINE)),
            ("Copy \\[...\\]", lambda: self.copy_latex(CopyFormat.DISPLAY)),
            ("Copy equation", lambda: self.copy_latex(CopyFormat.EQUATION)),
        )
        for label, callback in buttons:
            button = QPushButton(label)
            button.clicked.connect(callback)
            button_layout.addWidget(button)
            if label == "Run OCR":
                self.run_ocr_button = button

        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(140)
        self.history_list.itemDoubleClicked.connect(self._restore_history_item)

        layout = QVBoxLayout()
        layout.addWidget(splitter, 1)
        layout.addLayout(button_layout)
        layout.addWidget(QLabel("History — double click to restore"))
        layout.addWidget(self.history_list)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _build_actions(self) -> None:
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_image_dialog)

        paste_action = QAction("Paste image", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_image)

        run_action = QAction("Run OCR", self)
        run_action.setShortcut(QKeySequence("Ctrl+Return"))
        run_action.triggered.connect(self.run_ocr)

        self.addActions([open_action, paste_action, run_action])

    def open_image_dialog(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open equation image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if filename:
            self.load_image_file(Path(filename))

    def load_image_file(self, path: Path) -> None:
        try:
            image = Image.open(path).convert("RGB")
        except Exception as exc:
            QMessageBox.warning(self, "Image error", f"이미지를 열 수 없습니다.\n{exc}")
            return
        self._set_image(image)
        self.statusBar().showMessage(str(path), 5000)

    def paste_image(self) -> None:
        from PySide6.QtWidgets import QApplication

        qimage = QApplication.clipboard().image()
        if qimage.isNull():
            QMessageBox.information(self, "Clipboard", "Clipboard에 이미지가 없습니다.")
            return
        try:
            self._set_image(qimage_to_pil(qimage).convert("RGB"))
        except Exception as exc:
            QMessageBox.warning(self, "Clipboard error", str(exc))

    def run_ocr(self) -> None:
        if self._image is None:
            QMessageBox.information(self, "OCR", "먼저 수식 이미지를 넣어주세요.")
            return
        if self._ocr_busy:
            return
        self._ocr_busy = True
        self.run_ocr_button.setEnabled(False)
        self.statusBar().showMessage("OCR 실행 중… 모델 최초 로딩은 시간이 더 걸릴 수 있습니다.")
        self.recognize_requested.emit(self._image.copy())

    def copy_latex(self, copy_format: CopyFormat) -> None:
        from PySide6.QtWidgets import QApplication

        text = self.latex_edit.toPlainText()
        if not text.strip():
            return
        QApplication.clipboard().setText(format_latex(text, copy_format))
        self.statusBar().showMessage(f"Copied: {copy_format.value}", 2500)

    def _set_image(self, image: Image.Image) -> None:
        self._image = image
        qimage = ImageQt(image)
        self.image_view.set_image(QPixmap.fromImage(qimage))
        self.statusBar().showMessage(f"Image loaded: {image.width}×{image.height}", 3000)

    def _on_ocr_completed(self, latex: str) -> None:
        self._ocr_busy = False
        self.run_ocr_button.setEnabled(True)
        self.latex_edit.setPlainText(latex)
        self._history.add(latex)
        self._reload_history()
        self.statusBar().showMessage("OCR 완료", 3000)

    def _on_ocr_failed(self, message: str) -> None:
        self._ocr_busy = False
        self.run_ocr_button.setEnabled(True)
        QMessageBox.critical(self, "OCR failed", message)
        self.statusBar().showMessage("OCR 실패", 3000)

    def _refresh_preview(self) -> None:
        latex = self.latex_edit.toPlainText().strip()
        if not latex:
            self.preview.setText("LaTeX preview")
            self.preview.setPixmap(QPixmap())
            return
        try:
            image = render_latex_preview(latex)
            self.preview.setPixmap(QPixmap.fromImage(ImageQt(image)))
            self.preview.setText("")
        except Exception as exc:
            self.preview.setPixmap(QPixmap())
            self.preview.setText(f"Preview unavailable\n{exc}")

    def _reload_history(self) -> None:
        self.history_list.clear()
        for entry in self._history.recent():
            item_text = entry.latex.replace("\n", " ")
            if len(item_text) > 110:
                item_text = item_text[:107] + "..."
            self.history_list.addItem(item_text)
            self.history_list.item(self.history_list.count() - 1).setData(
                Qt.ItemDataRole.UserRole,
                entry.latex,
            )

    def _restore_history_item(self, item) -> None:
        latex = item.data(Qt.ItemDataRole.UserRole)
        self.latex_edit.setPlainText(latex)


def _history_path() -> Path:
    data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    return Path(data_dir) / "history.sqlite3"
