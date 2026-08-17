from __future__ import annotations

import signal
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from formula_ocr.input.global_hotkey import DEFAULT_HOTKEY_LABEL, GlobalHotkeyManager
from formula_ocr.runtime.webengine import configure_webengine_environment
from formula_ocr.ui.latex_preview import install_latex_preview
from formula_ocr.ui.main_window import MainWindow
from formula_ocr.ui.theme import APP_STYLESHEET


def main() -> int:
    configure_webengine_environment()

    app = QApplication(sys.argv)
    app.setApplicationName("Formula OCR")
    app.setOrganizationName("FormulaOCR")
    app.setStyleSheet(APP_STYLESHEET)

    window = MainWindow()
    install_latex_preview(window)
    window.show()

    global_hotkey = GlobalHotkeyManager(app)
    global_hotkey.activated.connect(window.capture_area)
    hotkey_support = global_hotkey.start()
    if hotkey_support.supported:
        window.statusBar().showMessage(
            f"Global capture ready · {DEFAULT_HOTKEY_LABEL}",
            5000,
        )
    else:
        window.statusBar().showMessage(hotkey_support.message, 7000)
    app.aboutToQuit.connect(global_hotkey.stop)

    # Qt event loop 중에도 Python signal handler가 주기적으로 실행될 기회를 준다.
    signal_timer = QTimer(app)
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start(200)

    def request_shutdown(signum, frame) -> None:
        window.request_close()

    signal.signal(signal.SIGINT, request_shutdown)
    signal.signal(signal.SIGTERM, request_shutdown)
    return app.exec()
