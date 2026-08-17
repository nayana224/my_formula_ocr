from formula_ocr.input.global_hotkey import detect_hotkey_support


def test_windows_supports_global_hotkey() -> None:
    support = detect_hotkey_support(platform_name="win32", session_type="", display="")

    assert support.supported is True
    assert support.backend == "win32"


def test_linux_x11_supports_global_hotkey() -> None:
    support = detect_hotkey_support(
        platform_name="linux",
        session_type="x11",
        display=":0",
    )

    assert support.supported is True
    assert support.backend == "x11"


def test_linux_wayland_disables_pynput_global_hotkey() -> None:
    support = detect_hotkey_support(
        platform_name="linux",
        session_type="wayland",
        display=":0",
    )

    assert support.supported is False
    assert support.backend == "wayland"


def test_linux_without_display_is_not_supported() -> None:
    support = detect_hotkey_support(
        platform_name="linux",
        session_type="x11",
        display="",
    )

    assert support.supported is False
