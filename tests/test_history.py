from formula_ocr.history.database import HistoryDatabase


def test_history_keeps_most_recent_entries(tmp_path) -> None:
    database = HistoryDatabase(tmp_path / "history.sqlite3")
    database.add("x")
    database.add("y")

    entries = database.recent()

    assert [entry.latex for entry in entries] == ["y", "x"]


def test_history_ignores_empty_latex(tmp_path) -> None:
    database = HistoryDatabase(tmp_path / "history.sqlite3")
    database.add("   ")

    assert database.recent() == []
