from __future__ import annotations

from pathlib import Path

from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6.QtCore import QSettings, QStandardPaths, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QAction, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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

from formula_ocr.capture.area_selector import ScreenAreaSelector
from formula_ocr.capture.clipboard import qimage_to_pil
from formula_ocr.history.database import HistoryDatabase, HistoryEntry
from formula_ocr.latex.formatter import CopyFormat, format_latex
from formula_ocr.latex.renderer import render_latex_preview
from formula_ocr.ocr.pix2tex_engine import Pix2TexEngine
from formula_ocr.ocr.result_quality import looks_suspicious_formula_result
from formula_ocr.ui.image_view import ImageView
from formula_ocr.ui.ocr_worker import OcrWorker


_COPY_FORMATS = (
    ("Raw LaTeX", CopyFormat.LATEX),
    ("Inline  $...$", CopyFormat.INLINE),
    ("Display  \\[...\\]", CopyFormat.DISPLAY),
    ("Equation", CopyFormat.EQUATION),
)


class MainWindow(QMainWindow):
    recognize_requested = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._image: Image.Image | None = None
        self._ocr_busy = False
        self._close_after_ocr = False
        self._capture_overlay: ScreenAreaSelector | None = None
        self._settings = QSettings()
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
        self.resize(1240, 800)
        self.setMinimumSize(900, 620)
        self.setStatusBar(QStatusBar(self))
        self._build_ui()
        self._build_actions()
        self._load_preferences()
        self._reload_history()

    def closeEvent(self, event) -> None:
        if self._ocr_busy:
            self._close_after_ocr = True
            self.statusBar().showMessage("OCR 완료 후 안전하게 종료합니다.")
            event.ignore()
            return
        self._worker_thread.quit()
        self._worker_thread.wait()
        super().closeEvent(event)

    def request_close(self) -> None:
        """SIGINT/SIGTERM에서도 worker를 강제 종료하지 않고 앱을 닫는다."""
        if self._ocr_busy:
            self._close_after_ocr = True
            self.statusBar().showMessage("종료 요청됨 · OCR 완료 후 종료합니다.")
            return
        self.close()

    def _build_ui(self) -> None:
        self.image_view = ImageView()
        self.image_view.image_file_dropped.connect(self.load_image_file)

        self.latex_edit = QPlainTextEdit()
        self.latex_edit.setPlaceholderText("인식된 LaTeX를 여기에서 바로 수정할 수 있습니다.")
        self.latex_edit.setMinimumHeight(90)
        self.latex_edit.setMaximumHeight(140)
        self.latex_edit.textChanged.connect(self._refresh_preview)

        self.preview = QLabel("Rendered preview")
        self.preview.setObjectName("preview")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(280)

        self.formula_warning = QLabel()
        self.formula_warning.setObjectName("formulaWarning")
        self.formula_warning.setWordWrap(True)
        self.formula_warning.setVisible(False)

        image_card = self._make_card("Source", self.image_view)

        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(18, 16, 18, 18)
        result_layout.setSpacing(10)
        result_layout.addWidget(self._section_label("Rendered Preview"))
        result_layout.addWidget(self.preview, 3)
        result_layout.addWidget(self.formula_warning)
        result_layout.addWidget(self._section_label("LaTeX · editable"))
        result_layout.addWidget(self.latex_edit, 1)
        result_card = QFrame()
        result_card.setObjectName("card")
        result_card.setLayout(result_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(image_card)
        splitter.addWidget(result_card)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)
        splitter.setSizes([470, 700])

        self.capture_button = QPushButton("Capture Area")
        self.capture_button.setObjectName("primaryButton")
        self.capture_button.setToolTip("Ctrl+Shift+X · 영역 선택 후 OCR")
        self.capture_button.clicked.connect(self.capture_area)

        open_button = QPushButton("Open Image")
        open_button.clicked.connect(self.open_image_dialog)
        paste_button = QPushButton("Paste Image")
        paste_button.clicked.connect(self.paste_image)

        self.run_ocr_button = QPushButton("Run OCR")
        self.run_ocr_button.clicked.connect(self.run_ocr)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        action_layout.addWidget(self.capture_button)
        action_layout.addWidget(open_button)
        action_layout.addWidget(paste_button)
        action_layout.addWidget(self.run_ocr_button)
        action_layout.addStretch(1)

        self.auto_ocr_check = QCheckBox("Auto OCR")
        self.auto_ocr_check.setToolTip("Open/Paste/Drop 직후 자동으로 OCR을 실행합니다.")
        self.auto_ocr_check.toggled.connect(self._save_preferences)

        self.auto_copy_check = QCheckBox("Auto Copy")
        self.auto_copy_check.setToolTip("OCR 성공 직후 선택한 형식을 clipboard에 복사합니다.")
        self.auto_copy_check.toggled.connect(self._save_preferences)

        self.output_format = QComboBox()
        for label, copy_format in _COPY_FORMATS:
            self.output_format.addItem(label, copy_format.value)
        self.output_format.currentIndexChanged.connect(self._save_preferences)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self.copy_selected_format)

        automation_layout = QHBoxLayout()
        automation_layout.setSpacing(10)
        automation_layout.addWidget(self.auto_ocr_check)
        automation_layout.addWidget(self.auto_copy_check)
        automation_layout.addStretch(1)
        automation_layout.addWidget(QLabel("Output"))
        automation_layout.addWidget(self.output_format)
        automation_layout.addWidget(copy_button)

        formula_tip = QLabel(
            "Formula mode · 자연어 문장보다 수식 영역만 선택하면 인식 정확도가 높아집니다."
        )
        formula_tip.setObjectName("hintLabel")

        controls_card = QFrame()
        controls_card.setObjectName("card")
        controls_layout = QVBoxLayout(controls_card)
        controls_layout.setContentsMargins(14, 12, 14, 12)
        controls_layout.setSpacing(10)
        controls_layout.addLayout(action_layout)
        controls_layout.addLayout(automation_layout)
        controls_layout.addWidget(formula_tip)

        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("Search history")
        self.history_search.setClearButtonEnabled(True)
        self.history_search.textChanged.connect(self._reload_history)

        favorite_button = QPushButton("Favorite")
        favorite_button.clicked.connect(self._toggle_selected_favorite)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self._delete_selected_history)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self._clear_history)

        history_controls = QHBoxLayout()
        history_controls.setSpacing(8)
        history_controls.addWidget(self.history_search, 1)
        history_controls.addWidget(favorite_button)
        history_controls.addWidget(delete_button)
        history_controls.addWidget(clear_button)

        self.history_list = QListWidget()
        self.history_list.setMinimumHeight(105)
        self.history_list.setMaximumHeight(160)
        self.history_list.itemDoubleClicked.connect(self._restore_history_item)

        history_layout = QVBoxLayout()
        history_layout.setContentsMargins(14, 12, 14, 14)
        history_layout.setSpacing(8)
        history_layout.addWidget(self._section_label("History · double click to restore"))
        history_layout.addLayout(history_controls)
        history_layout.addWidget(self.history_list)
        history_card = QFrame()
        history_card.setObjectName("card")
        history_card.setLayout(history_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(splitter, 1)
        layout.addWidget(controls_card)
        layout.addWidget(history_card)
        central = QWidget()
        central.setObjectName("root")
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _build_actions(self) -> None:
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_image_dialog)

        paste_action = QAction("Paste image", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_image)

        capture_action = QAction("Capture area", self)
        capture_action.setShortcut(QKeySequence("Ctrl+Shift+X"))
        capture_action.triggered.connect(self.capture_area)

        run_action = QAction("Run OCR", self)
        run_action.setShortcut(QKeySequence("Ctrl+Return"))
        run_action.triggered.connect(self.run_ocr)

        copy_action = QAction("Copy output", self)
        copy_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        copy_action.triggered.connect(self.copy_selected_format)

        self.addActions([open_action, paste_action, capture_action, run_action, copy_action])

    def _make_card(self, title: str, widget: QWidget) -> QFrame:
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(10)
        layout.addWidget(self._section_label(title))
        layout.addWidget(widget, 1)
        card = QFrame()
        card.setObjectName("card")
        card.setLayout(layout)
        return card

    def _section_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("sectionLabel")
        return label

    def _load_preferences(self) -> None:
        self.auto_ocr_check.setChecked(self._settings.value("auto_ocr", True, bool))
        self.auto_copy_check.setChecked(self._settings.value("auto_copy", True, bool))
        stored_format = self._settings.value("copy_format", CopyFormat.LATEX.value, str)
        for index in range(self.output_format.count()):
            if self.output_format.itemData(index) == stored_format:
                self.output_format.setCurrentIndex(index)
                break

    def _save_preferences(self) -> None:
        if not hasattr(self, "auto_ocr_check"):
            return
        self._settings.setValue("auto_ocr", self.auto_ocr_check.isChecked())
        self._settings.setValue("auto_copy", self.auto_copy_check.isChecked())
        self._settings.setValue("copy_format", self._selected_copy_format().value)

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
        if self._ocr_busy:
            self.statusBar().showMessage("OCR 실행 중입니다. 완료 후 새 이미지를 넣어주세요.", 3000)
            return
        try:
            image = Image.open(path).convert("RGB")
        except Exception as exc:
            QMessageBox.warning(self, "Image error", f"이미지를 열 수 없습니다.\n{exc}")
            return
        self._set_image(image)
        self.statusBar().showMessage(str(path), 3000)
        self._run_ocr_if_enabled()

    def paste_image(self) -> None:
        from PySide6.QtWidgets import QApplication

        if self._ocr_busy:
            self.statusBar().showMessage("OCR 실행 중입니다. 완료 후 붙여넣어주세요.", 3000)
            return
        qimage = QApplication.clipboard().image()
        if qimage.isNull():
            QMessageBox.information(self, "Clipboard", "Clipboard에 이미지가 없습니다.")
            return
        try:
            self._set_image(qimage_to_pil(qimage).convert("RGB"))
        except Exception as exc:
            QMessageBox.warning(self, "Clipboard error", str(exc))
            return
        self._run_ocr_if_enabled()

    def capture_area(self) -> None:
        if self._ocr_busy:
            self.statusBar().showMessage("OCR 실행 중에는 화면 캡처를 시작할 수 없습니다.", 3000)
            return
        self.hide()
        QTimer.singleShot(200, self._show_capture_overlay)

    def _show_capture_overlay(self) -> None:
        try:
            overlay = ScreenAreaSelector()
        except Exception as exc:
            self.show()
            QMessageBox.warning(self, "Capture error", f"화면 캡처를 시작할 수 없습니다.\n{exc}")
            return

        self._capture_overlay = overlay
        overlay.captured.connect(self._on_area_captured)
        overlay.cancelled.connect(self._on_capture_cancelled)
        overlay.show()

    def _on_area_captured(self, pixmap: QPixmap) -> None:
        self._capture_overlay = None
        self.show()
        self.raise_()
        self.activateWindow()
        try:
            image = qimage_to_pil(pixmap.toImage()).convert("RGB")
        except Exception as exc:
            QMessageBox.warning(self, "Capture error", f"선택 영역을 읽을 수 없습니다.\n{exc}")
            return
        self._set_image(image)
        self._start_ocr()

    def _on_capture_cancelled(self) -> None:
        self._capture_overlay = None
        self.show()
        self.raise_()
        self.activateWindow()
        self.statusBar().showMessage("화면 캡처 취소", 2000)

    def _run_ocr_if_enabled(self) -> None:
        if self.auto_ocr_check.isChecked():
            self._start_ocr()

    def run_ocr(self) -> None:
        self._start_ocr()

    def _start_ocr(self) -> None:
        if self._image is None:
            QMessageBox.information(self, "OCR", "먼저 수식 이미지를 넣어주세요.")
            return
        if self._ocr_busy:
            return
        self._ocr_busy = True
        self._set_busy_state(True)
        self.statusBar().showMessage("OCR 실행 중… 모델 최초 로딩은 시간이 더 걸릴 수 있습니다.")
        self.recognize_requested.emit(self._image.copy())

    def _set_busy_state(self, busy: bool) -> None:
        self.run_ocr_button.setEnabled(not busy)
        self.capture_button.setEnabled(not busy)
        self.run_ocr_button.setText("Recognizing…" if busy else "Run OCR")

    def _selected_copy_format(self) -> CopyFormat:
        value = self.output_format.currentData()
        try:
            return CopyFormat(value)
        except ValueError:
            return CopyFormat.LATEX

    def copy_selected_format(self) -> None:
        self.copy_latex(self._selected_copy_format())

    def copy_latex(self, copy_format: CopyFormat) -> None:
        from PySide6.QtWidgets import QApplication

        text = self.latex_edit.toPlainText()
        if not text.strip():
            return
        QApplication.clipboard().setText(format_latex(text, copy_format))
        self.statusBar().showMessage(f"Copied · {copy_format.value}", 2500)

    def _set_image(self, image: Image.Image) -> None:
        self._image = image
        qimage = ImageQt(image)
        self.image_view.set_image(QPixmap.fromImage(qimage))
        self.statusBar().showMessage(f"Image loaded · {image.width}×{image.height}", 2500)

    def _on_ocr_completed(self, latex: str) -> None:
        self._ocr_busy = False
        self._set_busy_state(False)
        self.latex_edit.setPlainText(latex)
        self._history.add(latex)
        self._reload_history()
        if self.auto_copy_check.isChecked():
            self.copy_selected_format()
            self.statusBar().showMessage("OCR complete · copied to clipboard", 3000)
        else:
            self.statusBar().showMessage("OCR complete", 3000)
        self._finish_pending_close()

    def _on_ocr_failed(self, message: str) -> None:
        self._ocr_busy = False
        self._set_busy_state(False)
        QMessageBox.critical(self, "OCR failed", message)
        self.statusBar().showMessage("OCR 실패", 3000)
        self._finish_pending_close()

    def _finish_pending_close(self) -> None:
        if not self._close_after_ocr:
            return
        self._close_after_ocr = False
        QTimer.singleShot(0, self.close)

    def _refresh_preview(self) -> None:
        latex = self.latex_edit.toPlainText().strip()
        self._refresh_formula_warning(latex)
        if not latex:
            self.preview.setText("Rendered preview")
            self.preview.setPixmap(QPixmap())
            return
        try:
            image = render_latex_preview(latex)
            self.preview.setPixmap(QPixmap.fromImage(ImageQt(image)))
            self.preview.setText("")
        except Exception as exc:
            self.preview.setPixmap(QPixmap())
            self.preview.setText(f"Preview unavailable\n{exc}")

    def _refresh_formula_warning(self, latex: str) -> None:
        suspicious = looks_suspicious_formula_result(latex)
        self.formula_warning.setVisible(suspicious)
        if suspicious:
            self.formula_warning.setText(
                "수식이 아닌 자연어가 함께 선택된 것 같습니다. "
                "Formula mode에서는 수식 부분만 다시 캡처하면 정확도가 높아집니다."
            )
        else:
            self.formula_warning.clear()

    def _reload_history(self) -> None:
        self.history_list.clear()
        query = self.history_search.text() if hasattr(self, "history_search") else ""
        for entry in self._history.recent(query=query):
            prefix = "★  " if entry.favorite else ""
            item_text = prefix + entry.latex.replace("\n", " ")
            if len(item_text) > 110:
                item_text = item_text[:107] + "..."
            self.history_list.addItem(item_text)
            self.history_list.item(self.history_list.count() - 1).setData(
                Qt.ItemDataRole.UserRole,
                entry,
            )

    def _restore_history_item(self, item) -> None:
        entry = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(entry, HistoryEntry):
            self.latex_edit.setPlainText(entry.latex)

    def _selected_history_entry(self) -> HistoryEntry | None:
        item = self.history_list.currentItem()
        if item is None:
            return None
        entry = item.data(Qt.ItemDataRole.UserRole)
        return entry if isinstance(entry, HistoryEntry) else None

    def _toggle_selected_favorite(self) -> None:
        entry = self._selected_history_entry()
        if entry is None:
            return
        self._history.set_favorite(entry.id, not entry.favorite)
        self._reload_history()

    def _delete_selected_history(self) -> None:
        entry = self._selected_history_entry()
        if entry is None:
            return
        self._history.delete(entry.id)
        self._reload_history()

    def _clear_history(self) -> None:
        if self.history_list.count() == 0:
            return
        answer = QMessageBox.question(
            self,
            "Clear history",
            "저장된 OCR History를 모두 삭제할까요?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._history.clear()
        self._reload_history()


def _history_path() -> Path:
    data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    return Path(data_dir) / "history.sqlite3"
