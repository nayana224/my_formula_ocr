from __future__ import annotations

import signal
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from formula_ocr.ui.main_window import MainWindow
from formula_ocr.ui.theme import APP_STYLESHEET


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Formula OCR")
    app.setOrganizationName("FormulaOCR")
    app.setStyleSheet(APP_STYLESHEET)

    window = MainWindow()
    window.show()

    # Qt event loop 중에도 Python signal handler가 주기적으로 실행될 기회를 준다.
    signal_timer = QTimer(app)
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start(200)

    def request_shutdown(signum, frame) -> None:
        window.request_close()

    signal.signal(signal.SIGINT, request_shutdown)
    signal.signal(signal.SIGTERM, request_shutdown)
    return app.exec()
