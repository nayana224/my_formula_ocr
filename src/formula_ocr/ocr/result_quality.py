from __future__ import annotations


_RARE_COMMANDS = (
    r"\beth",
    r"\daleth",
    r"\gimel",
    r"\mathfrak",
    r"\mho",
    r"\varpi",
    r"\wp",
)


def looks_suspicious_formula_result(latex: str) -> bool:
    """자연어가 수식으로 오인된 흔적이 강한 결과만 보수적으로 감지한다."""
    clean = latex.strip()
    if not clean:
        return False

    rare_count = sum(clean.count(command) for command in _RARE_COMMANDS)
    if rare_count >= 2:
        return True

    operator_count = clean.count(r"\operatorname")
    return rare_count >= 1 and operator_count >= 2
