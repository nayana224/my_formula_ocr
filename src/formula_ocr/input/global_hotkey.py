from __future__ import annotations

import os
import sys
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal


DEFAULT_HOTKEY = "<ctrl>+<alt>+m"
DEFAULT_HOTKEY_LABEL = "Ctrl+Alt+M"


@dataclass(frozen=True)
class HotkeySupport:
    supported: bool
    backend: str
    message: str


def detect_hotkey_support(
    platform_name: str | None = None,
    session_type: str | None = None,
    display: str | None = None,
) -> HotkeySupport:
    """현재 데스크톱에서 pynput 전역 단축키 사용 가능 여부를 판정한다."""
    platform_name = platform_name or sys.platform
    session_type = (session_type or os.environ.get("XDG_SESSION_TYPE", "")).lower()
    display = display if display is not None else os.environ.get("DISPLAY", "")

    if platform_name.startswith("win"):
        return HotkeySupport(True, "win32", "Global hotkey ready")

    if platform_name.startswith("linux"):
        if session_type == "wayland":
            return HotkeySupport(
                False,
                "wayland",
                "Wayland에서는 현재 전역 단축키를 자동 등록하지 않습니다.",
            )
        if display:
            return HotkeySupport(True, "x11", "Global hotkey ready")
        return HotkeySupport(
            False,
            "linux",
            "X11 DISPLAY를 찾을 수 없어 전역 단축키를 사용할 수 없습니다.",
        )

    return HotkeySupport(
        False,
        platform_name,
        "현재 운영체제에서는 전역 단축키를 지원하지 않습니다.",
    )


class GlobalHotkeyManager(QObject):
    """pynput listener와 Qt UI 사이를 Signal로 안전하게 연결한다."""

    activated = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._listener = None
        self._support = detect_hotkey_support()

    @property
    def support(self) -> HotkeySupport:
        return self._support

    @property
    def running(self) -> bool:
        return self._listener is not None

    def start(self) -> HotkeySupport:
        if self.running:
            return self._support
        if not self._support.supported:
            return self._support

        try:
            from pynput import keyboard

            listener = keyboard.GlobalHotKeys({DEFAULT_HOTKEY: self._emit_activated})
            listener.start()
        except Exception as exc:
            self._support = HotkeySupport(
                False,
                self._support.backend,
                f"Global hotkey 시작 실패: {exc}",
            )
            return self._support

        self._listener = listener
        self._support = HotkeySupport(
            True,
            self._support.backend,
            f"{DEFAULT_HOTKEY_LABEL} · global capture ready",
        )
        return self._support

    def stop(self) -> None:
        listener = self._listener
        self._listener = None
        if listener is None:
            return
        try:
            listener.stop()
        except Exception:
            pass

    def _emit_activated(self) -> None:
        # pynput callback thread에서 UI를 직접 만지지 않고 Qt signal만 발생시킨다.
        self.activated.emit()
