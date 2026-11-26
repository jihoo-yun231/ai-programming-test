import importlib.util
import re
from pathlib import Path


MODULE_PATH = Path(__file__).parent / "week11_files" / "load_scores.py"
spec = importlib.util.spec_from_file_location("load_scores", MODULE_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load module from {MODULE_PATH}")
load_scores_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(load_scores_module)
load_scores = load_scores_module.load_scores


def _assert_reported_reason(output, line_no, keywords):
    line_pattern = re.compile(rf"(?<!\d){line_no}(?!\d)")
    matching_lines = [
        line for line in output.splitlines() if line_pattern.search(line)
    ]
    assert matching_lines, f"line {line_no} was not reported"
    assert any(
        any(keyword.casefold() in line.casefold() for keyword in keywords)
        for line in matching_lines
    ), f"reason for line {line_no} was not reported"


def test_load_scores_returns_valid_rows_and_accepts_quoted_comma_in_name(
    tmp_path,
):
    csv_file = tmp_path / "scores.csv"
    csv_file.write_text(
        "name,score\n"
        '"최, 네번",90\n'
        "Lowest,0\n"
        "Highest,100\n",
        encoding="utf-8",
    )

    assert load_scores(csv_file) == [
        ("최, 네번", 90),
        ("Lowest", 0),
        ("Highest", 100),
    ]


def test_load_scores_returns_empty_list_for_empty_or_header_only_file(
    tmp_path,
):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")
    header_only_file = tmp_path / "header_only.csv"
    header_only_file.write_text("name,score\n", encoding="utf-8")

    assert load_scores(empty_file) == []
    assert load_scores(header_only_file) == []


def test_load_scores_skips_and_reports_invalid_rows(tmp_path, capsys):
    csv_file = tmp_path / "mixed.csv"
    csv_file.write_text(
        "name,score\n"
        ",12\n"
        "BlankScore,\n"
        "WhitespaceScore,   \n"
        "TooHigh,105\n"
        "Negative,-1\n"
        "NotNumber,abc\n"
        "TooFew\n"
        "TooMany,80,extra\n"
        "\n"
        "Duplicate,80\n"
        "Duplicate,90\n"
        '"최, 네번",50\n',
        encoding="utf-8",
    )

    kept = load_scores(csv_file)

    assert kept in (
        [("Duplicate", 80), ("최, 네번", 50)],
        [("Duplicate", 80), ("Duplicate", 90), ("최, 네번", 50)],
    )
    captured = capsys.readouterr()
    output = captured.out + captured.err
    _assert_reported_reason(output, 2, ("이름", "name"))
    _assert_reported_reason(output, 3, ("점수", "score"))
    _assert_reported_reason(output, 4, ("점수", "score"))
    _assert_reported_reason(output, 5, ("점수", "score"))
    _assert_reported_reason(output, 6, ("점수", "score"))
    _assert_reported_reason(output, 7, ("점수", "score"))
    _assert_reported_reason(output, 8, ("열", "column"))
    _assert_reported_reason(output, 9, ("열", "column"))
    _assert_reported_reason(output, 12, ("중복", "duplicate"))


def test_load_scores_handles_missing_file_and_directory_without_raising(
    tmp_path, capsys
):
    missing_file = tmp_path / "missing.csv"
    directory = tmp_path / "scores_folder"
    directory.mkdir()

    load_scores(missing_file)
    load_scores(directory)

    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert str(missing_file) in output
    assert str(directory) in output
