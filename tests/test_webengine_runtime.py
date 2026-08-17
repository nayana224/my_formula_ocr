from formula_ocr.runtime.webengine import configure_webengine_environment


def test_adds_disable_gpu_on_linux() -> None:
    environ = {}

    configure_webengine_environment(environ, platform="linux")

    assert environ["QTWEBENGINE_CHROMIUM_FLAGS"] == "--disable-gpu"


def test_preserves_existing_chromium_flags() -> None:
    environ = {"QTWEBENGINE_CHROMIUM_FLAGS": "--remote-debugging-port=9222"}

    configure_webengine_environment(environ, platform="linux")

    assert environ["QTWEBENGINE_CHROMIUM_FLAGS"] == (
        "--remote-debugging-port=9222 --disable-gpu"
    )


def test_does_not_duplicate_disable_gpu() -> None:
    environ = {"QTWEBENGINE_CHROMIUM_FLAGS": "--disable-gpu"}

    configure_webengine_environment(environ, platform="linux")

    assert environ["QTWEBENGINE_CHROMIUM_FLAGS"] == "--disable-gpu"


def test_does_not_change_non_linux_environment() -> None:
    environ = {"QTWEBENGINE_CHROMIUM_FLAGS": "--existing"}

    configure_webengine_environment(environ, platform="win32")

    assert environ["QTWEBENGINE_CHROMIUM_FLAGS"] == "--existing"
