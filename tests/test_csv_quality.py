import json

import pandas as pd
import pytest

from csv_quality import analyze_csv


def test_report_counts_rows_columns_missing_and_duplicates(tmp_path):
    csv_file = tmp_path / "customers.csv"
    csv_file.write_text(
        "name,age,city\nAsha,20,Varanasi\nRavi,,Lucknow\nAsha,20,Varanasi\n",
        encoding="utf-8",
    )

    report = analyze_csv(csv_file)

    assert report["row_count"] == 3
    assert report["column_count"] == 3
    assert report["duplicate_row_count"] == 1
    assert report["missing_values_by_column"]["age"] == 1
    assert report["numeric_summary"]["age"]["mean"] == pytest.approx(20.0)


def test_nonexistent_file_raises_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="Input file not found"):
        analyze_csv(tmp_path / "missing.csv")


def test_non_csv_file_is_rejected(tmp_path):
    file_path = tmp_path / "data.txt"
    file_path.write_text("a,b\n1,2\n", encoding="utf-8")

    with pytest.raises(ValueError, match=r"\.csv extension"):
        analyze_csv(file_path)


def test_zero_byte_file_is_rejected(tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV is empty"):
        analyze_csv(file_path)


def test_header_only_file_returns_zero_rows_and_json_safe_report(tmp_path):
    file_path = tmp_path / "headers.csv"
    file_path.write_text("name,score\n", encoding="utf-8")

    report = analyze_csv(file_path)

    assert report["row_count"] == 0
    assert report["column_count"] == 2
    # The report can be serialized without NaN/Infinity values.
    json.dumps(report, allow_nan=False)


def test_empty_numeric_column_has_null_statistics(tmp_path):
    file_path = tmp_path / "no_scores.csv"
    file_path.write_text("score\n,\n,\n", encoding="utf-8")

    report = analyze_csv(file_path)

    assert report["numeric_summary"]["score"]["min"] is None
    assert report["numeric_summary"]["score"]["mean"] is None
