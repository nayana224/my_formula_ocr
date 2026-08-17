from __future__ import annotations

import html

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QStackedLayout, QWidget


_KATEX_VERSION = "0.17.0"


class LatexPreviewWidget(QWidget):
    """KaTeX를 우선 사용하고 기존 pixmap을 fallback으로 유지한다."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._fallback = QLabel("Rendered preview")
        self._fallback.setObjectName("preview")
        self._fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._fallback.setMinimumHeight(310)

        self._web_view = None
        self._generation = 0
        self._stack = QStackedLayout(self)
        self._stack.setContentsMargins(0, 0, 0, 0)
        self._stack.addWidget(self._fallback)

        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
        except Exception:
            return

        try:
            web_view = QWebEngineView(self)
            web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            web_view.setMinimumHeight(310)
            web_view.loadFinished.connect(self._on_load_finished)
        except Exception:
            return

        self._web_view = web_view
        self._stack.addWidget(web_view)

    def setText(self, text: str) -> None:  # noqa: N802 - QLabel 호환 API
        self._fallback.setText(text)
        if not text.strip() or text == "Rendered preview":
            self._show_fallback()

    def setPixmap(self, pixmap: QPixmap) -> None:  # noqa: N802 - QLabel 호환 API
        self._fallback.setPixmap(pixmap)
        if self._web_view is None or pixmap.isNull():
            self._show_fallback()

    def set_latex(self, latex: str) -> None:
        """현재 LaTeX를 KaTeX로 렌더링하고 실패하면 fallback을 유지한다."""
        self._generation += 1
        if not latex.strip() or self._web_view is None:
            self._show_fallback()
            return

        # 비동기 KaTeX 로딩 동안에는 최신 mathtext 결과를 보여준다.
        self._show_fallback()
        self._web_view.setHtml(build_katex_html(latex))

    def _on_load_finished(self, success: bool) -> None:
        if not success or self._web_view is None:
            self._show_fallback()
            return

        generation = self._generation
        script = "window.__formulaOcrKatexStatus || 'unavailable'"

        def handle_status(status) -> None:
            if generation != self._generation:
                return
            if status == "ok":
                self._stack.setCurrentWidget(self._web_view)
            else:
                self._show_fallback()

        self._web_view.page().runJavaScript(script, handle_status)

    def _show_fallback(self) -> None:
        self._stack.setCurrentWidget(self._fallback)


def install_latex_preview(window) -> LatexPreviewWidget:
    """기존 MainWindow Preview QLabel을 호환 widget으로 교체한다."""
    old_preview = window.preview
    parent = old_preview.parentWidget()
    if parent is None or parent.layout() is None:
        raise RuntimeError("Preview layout을 찾을 수 없습니다.")

    preview = LatexPreviewWidget(parent)
    preview.setMinimumHeight(old_preview.minimumHeight())
    parent.layout().replaceWidget(old_preview, preview)
    old_preview.hide()
    old_preview.deleteLater()
    window.preview = preview

    window.latex_edit.textChanged.connect(
        lambda: preview.set_latex(window.latex_edit.toPlainText().strip())
    )
    preview.set_latex(window.latex_edit.toPlainText().strip())
    return preview


def build_katex_html(latex: str) -> str:
    """사용자 LaTeX를 HTML attribute로 escape해 안전한 KaTeX 문서를 만든다."""
    escaped = html.escape(latex, quote=True)
    css_url = (
        f"https://cdn.jsdelivr.net/npm/katex@{_KATEX_VERSION}/dist/"
        "katex.min.css"
    )
    js_url = (
        f"https://cdn.jsdelivr.net/npm/katex@{_KATEX_VERSION}/dist/"
        "katex.min.js"
    )
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="color-scheme" content="light">
<link rel="stylesheet" href="{css_url}" crossorigin="anonymous">
<style>
html, body {{ margin: 0; min-height: 100%; background: #fbfcfe; }}
body {{
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  box-sizing: border-box;
}}
#formula {{
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  font-size: 1.15rem;
}}
</style>
<script defer src="{js_url}" crossorigin="anonymous"></script>
</head>
<body>
<div id="formula" data-tex="{escaped}"></div>
<script>
window.addEventListener('load', function () {{
  const target = document.getElementById('formula');
  if (!window.katex) {{
    window.__formulaOcrKatexStatus = 'unavailable';
    return;
  }}
  try {{
    window.katex.render(target.dataset.tex, target, {{
      displayMode: true,
      throwOnError: true,
      strict: 'warn'
    }});
    window.__formulaOcrKatexStatus = 'ok';
  }} catch (error) {{
    window.__formulaOcrKatexStatus = 'error';
  }}
}});
</script>
</body>
</html>"""
