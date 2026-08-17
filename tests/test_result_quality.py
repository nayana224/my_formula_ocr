from formula_ocr.ocr.result_quality import looks_suspicious_formula_result


def test_normal_formula_is_not_suspicious() -> None:
    latex = r"i \sim \mathrm{Uniform}\{1,\dots,N\}"

    assert looks_suspicious_formula_result(latex) is False


def test_mixed_text_like_formula_is_suspicious() -> None:
    latex = (
        r"{\mathfrak{s}}\beth\varpi\mid"
        r"\operatorname{grasp}\operatorname{cycle}i^{\omega}\lambda"
    )

    assert looks_suspicious_formula_result(latex) is True


def test_single_rare_symbol_does_not_trigger_warning() -> None:
    latex = r"\mathfrak{g} + x"

    assert looks_suspicious_formula_result(latex) is False
