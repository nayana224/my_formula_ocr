from formula_ocr.latex.text_normalizer import text_to_latex


def test_removes_zero_width_and_recovers_common_sum_pattern() -> None:
    result = text_to_latex("L=N1\u200bi=1∑N\u200b(m^i\u200b−mi\u200b)2")

    assert result.latex == r"L=\frac{1}{N}\sum_{i=1}^{N}(m^i-mi)^{2}"
    assert result.warnings


def test_converts_unicode_super_and_subscripts() -> None:
    result = text_to_latex("x²+y₁")

    assert result.latex == "x^{2}+y_{1}"


def test_keeps_existing_latex_and_strips_math_delimiters() -> None:
    result = text_to_latex(r"\[ \frac{1}{N} \sum_{i=1}^{N} x_i \]")

    assert result.latex == r"\frac{1}{N} \sum_{i=1}^{N} x_i"
    assert result.warnings == ()


def test_converts_common_unicode_math_symbols() -> None:
    result = text_to_latex("α≤β→∞")

    assert result.latex == r"\alpha\leq\beta\to\infty"


def test_converts_simple_fraction() -> None:
    result = text_to_latex("L=1/N")

    assert result.latex == r"L=\frac{1}{N}"
