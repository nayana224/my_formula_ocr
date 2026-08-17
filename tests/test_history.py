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


def test_history_search_filters_latex(tmp_path) -> None:
    database = HistoryDatabase(tmp_path / "history.sqlite3")
    database.add(r"\frac{a}{b}")
    database.add(r"x_i")

    entries = database.recent(query="frac")

    assert [entry.latex for entry in entries] == [r"\frac{a}{b}"]


def test_favorite_entries_are_pinned(tmp_path) -> None:
    database = HistoryDatabase(tmp_path / "history.sqlite3")
    database.add("first")
    database.add("second")
    first_entry = database.recent()[-1]

    database.set_favorite(first_entry.id, True)
    entries = database.recent()

    assert entries[0].latex == "first"
    assert entries[0].favorite is True


def test_history_delete_removes_only_selected_entry(tmp_path) -> None:
    database = HistoryDatabase(tmp_path / "history.sqlite3")
    database.add("keep")
    database.add("delete")
    delete_entry = database.recent()[0]

    database.delete(delete_entry.id)

    assert [entry.latex for entry in database.recent()] == ["keep"]
