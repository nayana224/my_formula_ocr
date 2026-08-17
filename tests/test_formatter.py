import pytest

from formula_ocr.latex.formatter import CopyFormat, format_latex, normalize_latex


def test_normalize_latex_trims_surrounding_whitespace() -> None:
    assert normalize_latex("  x^2 + y^2  \n") == "x^2 + y^2"


@pytest.mark.parametrize(
    ("copy_format", "expected"),
    [
        (CopyFormat.LATEX, r"\frac{a}{b}"),
        (CopyFormat.INLINE, r"$\frac{a}{b}$"),
        (CopyFormat.DISPLAY, "\\[\n\\frac{a}{b}\n\\]"),
        (CopyFormat.MARKDOWN, "\\[\n\\frac{a}{b}\n\\]"),
        (
            CopyFormat.EQUATION,
            "\\begin{equation}\n\\frac{a}{b}\n\\end{equation}",
        ),
    ],
)
def test_format_latex(copy_format: CopyFormat, expected: str) -> None:
    assert format_latex(r"\frac{a}{b}", copy_format) == expected
