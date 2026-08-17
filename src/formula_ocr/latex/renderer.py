from __future__ import annotations

from io import BytesIO

from matplotlib.figure import Figure
from PIL import Image


def render_latex_preview(latex: str, dpi: int = 160) -> Image.Image:
    """matplotlib mathtext로 빠른 수식 미리보기를 만든다."""
    clean = latex.strip()
    if not clean:
        raise ValueError("미리볼 LaTeX가 비어 있습니다.")

    figure = Figure(figsize=(8, 1.6), dpi=dpi)
    figure.patch.set_alpha(0.0)
    axis = figure.add_axes((0, 0, 1, 1))
    axis.set_axis_off()
    axis.text(0.5, 0.5, f"${clean}$", ha="center", va="center", fontsize=18)

    buffer = BytesIO()
    figure.savefig(
        buffer,
        format="png",
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.15,
    )
    buffer.seek(0)
    return Image.open(buffer).copy()
