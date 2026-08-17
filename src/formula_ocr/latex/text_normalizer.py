from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


_ZERO_WIDTH = {"\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"}

_SYMBOLS = {
    "−": "-",
    "–": "-",
    "×": r"\times ",
    "÷": r"\div ",
    "±": r"\pm ",
    "∞": r"\infty ",
    "≤": r"\leq ",
    "≥": r"\geq ",
    "≠": r"\neq ",
    "≈": r"\approx ",
    "∈": r"\in ",
    "∉": r"\notin ",
    "→": r"\to ",
    "∂": r"\partial ",
    "∇": r"\nabla ",
    "∑": r"\sum ",
    "∏": r"\prod ",
}

_GREEK = {
    "α": r"\alpha ",
    "β": r"\beta ",
    "γ": r"\gamma ",
    "δ": r"\delta ",
    "ε": r"\epsilon ",
    "θ": r"\theta ",
    "λ": r"\lambda ",
    "μ": r"\mu ",
    "π": r"\pi ",
    "ρ": r"\rho ",
    "σ": r"\sigma ",
    "τ": r"\tau ",
    "φ": r"\phi ",
    "ω": r"\omega ",
}

_SUPERSCRIPT = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾", "0123456789+-()")
_SUBSCRIPT = str.maketrans("₀₁₂₃₄₅₆₇₈₉₊₋₍₎", "0123456789+-()")
_SUPER_CHARS = set("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾")
_SUB_CHARS = set("₀₁₂₃₄₅₆₇₈₉₊₋₍₎")


@dataclass(frozen=True)
class TextToLatexResult:
    latex: str
    warnings: tuple[str, ...] = ()


def text_to_latex(text: str) -> TextToLatexResult:
    """복사 과정에서 평탄화된 수식 텍스트를 보수적으로 LaTeX로 복구한다."""
    clean = _clean_input(text)
    if not clean:
        return TextToLatexResult("")

    if _looks_like_latex(clean):
        return TextToLatexResult(_strip_math_delimiters(clean))

    warnings: list[str] = []
    latex = _replace_script_characters(clean)

    # 렌더된 분수/시그마가 평탄화되며 N1i=1∑N 형태가 되는 흔한 경우를 복구한다.
    sigma_pattern = re.compile(r"([A-Za-z])1i=1∑\1")
    if sigma_pattern.search(latex):
        latex = sigma_pattern.sub(
            lambda match: rf"\frac{{1}}{{{match.group(1)}}}\sum_{{i=1}}^{{{match.group(1)}}}",
            latex,
        )
        warnings.append("분수와 합 기호의 배치는 복사된 문자 순서를 바탕으로 추정했습니다.")

    # 1/N, a/b처럼 피연산자가 단일 토큰인 경우만 안전하게 분수로 변환한다.
    simple_fraction = re.compile(r"(?<![A-Za-z0-9}])([A-Za-z0-9]+)\/([A-Za-z0-9]+)(?![A-Za-z0-9{])")
    latex = simple_fraction.sub(r"\\frac{\1}{\2}", latex)

    latex = _replace_symbols(latex)
    latex = re.sub(r"√\s*\(([^()]*)\)", r"\\sqrt{\1}", latex)
    latex = re.sub(r"√\s*([A-Za-z0-9]+)", r"\\sqrt{\1}", latex)

    # 닫는 괄호 바로 뒤의 숫자는 렌더된 위첨자가 평탄화된 경우가 많다.
    if re.search(r"\)(\d+)($|[^A-Za-z0-9])", latex):
        latex = re.sub(r"\)(\d+)($|[^A-Za-z0-9])", r")^{\1}\2", latex)
        warnings.append("괄호 뒤 숫자를 위첨자로 추정했습니다.")

    if re.search(r"(?<!\\)[A-Za-z]{2,}", latex):
        warnings.append("붙어 있는 영문자(mi 등)는 곱, 첨자, 변수명 중 무엇인지 확인이 필요합니다.")

    latex = _normalize_spacing(latex)
    return TextToLatexResult(latex, tuple(dict.fromkeys(warnings)))


def _clean_input(text: str) -> str:
    text = "".join(char for char in text if char not in _ZERO_WIDTH)
    text = unicodedata.normalize("NFC", text)
    return text.strip()


def _looks_like_latex(text: str) -> bool:
    return bool(re.search(r"\\[A-Za-z]+|\\[\[\]()]|\$.*\$", text, re.DOTALL))


def _strip_math_delimiters(text: str) -> str:
    clean = text.strip()
    pairs = (("$$", "$$"), (r"\[", r"\]"), (r"\(", r"\)"), ("$", "$"))
    for start, end in pairs:
        if clean.startswith(start) and clean.endswith(end) and len(clean) >= len(start) + len(end):
            return clean[len(start) : -len(end)].strip()
    return clean


def _replace_script_characters(text: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char in _SUPER_CHARS:
            end = index
            while end < len(text) and text[end] in _SUPER_CHARS:
                end += 1
            output.append("^{" + text[index:end].translate(_SUPERSCRIPT) + "}")
            index = end
            continue
        if char in _SUB_CHARS:
            end = index
            while end < len(text) and text[end] in _SUB_CHARS:
                end += 1
            output.append("_{" + text[index:end].translate(_SUBSCRIPT) + "}")
            index = end
            continue
        output.append(char)
        index += 1
    return "".join(output)


def _replace_symbols(text: str) -> str:
    for symbol, replacement in {**_SYMBOLS, **_GREEK}.items():
        text = text.replace(symbol, replacement)
    return text


def _normalize_spacing(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*([=+\-])\s*", r"\1", text)
    text = re.sub(
        r"\\(sum|prod|times|div|pm|infty|leq|geq|neq|approx|in|notin|to|partial|nabla|[a-z]+)\s+",
        r"\\\1",
        text,
    )
    return text.strip()
