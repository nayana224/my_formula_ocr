from enum import Enum


class CopyFormat(str, Enum):
    LATEX = "latex"
    INLINE = "inline"
    DISPLAY = "display"
    EQUATION = "equation"
    MARKDOWN = "markdown"


def normalize_latex(latex: str) -> str:
    return latex.strip()


def format_latex(latex: str, copy_format: CopyFormat) -> str:
    """선택한 형식에 맞게 LaTeX 문자열을 감싼다."""
    clean = normalize_latex(latex)
    if copy_format is CopyFormat.LATEX:
        return clean
    if copy_format is CopyFormat.INLINE:
        return f"${clean}$"
    if copy_format in (CopyFormat.DISPLAY, CopyFormat.MARKDOWN):
        return f"\\[\n{clean}\n\\]"
    if copy_format is CopyFormat.EQUATION:
        return f"\\begin{{equation}}\n{clean}\n\\end{{equation}}"
    raise ValueError(f"Unsupported copy format: {copy_format}")
