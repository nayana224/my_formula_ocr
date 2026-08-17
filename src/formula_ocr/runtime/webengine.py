from __future__ import annotations

import os
import sys
from collections.abc import MutableMapping


_DISABLE_GPU_FLAG = "--disable-gpu"


def configure_webengine_environment(
    environ: MutableMapping[str, str] | None = None,
    *,
    platform: str | None = None,
) -> None:
    """Linux Qt WebEngine에서 Chromium GPU 가속만 비활성화한다."""
    target = os.environ if environ is None else environ
    current_platform = sys.platform if platform is None else platform
    if not current_platform.startswith("linux"):
        return

    current_flags = target.get("QTWEBENGINE_CHROMIUM_FLAGS", "").strip()
    if _DISABLE_GPU_FLAG in current_flags.split():
        return

    target["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(
        value for value in (current_flags, _DISABLE_GPU_FLAG) if value
    )
