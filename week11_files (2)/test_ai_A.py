import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).parent / "week11_files" / "load_scores.py"
spec = importlib.util.spec_from_file_location("load_scores", MODULE_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load module from {MODULE_PATH}")
load_scores_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(load_scores_module)
load_scores = load_scores_module.load_scores


def test_load_scores_keeps_valid_scores_and_duplicate_names(tmp_path):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(
        "name,score\n"
        " Alice ,0\n"
        "Bob,100\n"
        "Same,70\n"
        "Same,88\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(csv_file)

    assert kept == [
        ("Alice", 0),
        ("Bob", 100),
        ("Same", 70),
        ("Same", 88),
    ]
    assert skipped == []


def test_load_scores_returns_empty_lists_for_header_only_file(tmp_path):
    csv_file = tmp_path / "header_only.csv"
    csv_file.write_text("name,score\n", encoding="utf-8")

    assert load_scores(csv_file) == ([], [])


def test_load_scores_records_invalid_rows_and_ignores_blank_lines(tmp_path):
    csv_file = tmp_path / "mixed.csv"
    csv_file.write_text(
        "name,score\n"
        "Alice,90\n"
        "\n"
        "OnlyName\n"
        "Too,many,columns\n"
        ",90\n"
        "Bob,\n"
        "Cara,nope\n"
        "Dan,1.5\n"
        "Eve,-1\n"
        "Frank,101\n"
        "   ,12\n",
        encoding="utf-8",
    )

    kept, skipped = load_scores(csv_file)

    assert kept == [("Alice", 90)]
    assert skipped == [
        (4, "OnlyName", "열 개수가 2가 아님"),
        (5, "Too,many,columns", "열 개수가 2가 아님"),
        (6, ",90", "이름이 비어 있음"),
        (7, "Bob,", "점수가 비어 있음"),
        (8, "Cara,nope", "점수가 정수가 아님"),
        (9, "Dan,1.5", "점수가 정수가 아님"),
        (10, "Eve,-1", "점수가 0~100 밖"),
        (11, "Frank,101", "점수가 0~100 밖"),
        (12, "   ,12", "이름이 비어 있음"),
    ]


def test_load_scores_propagates_file_not_found(tmp_path):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_scores(missing_file)
