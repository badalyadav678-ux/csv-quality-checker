"""Analyze a CSV file and report basic data-quality signals."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


def _json_number(value: Any) -> int | float | None:
    """Convert a Pandas/NumPy number into a JSON-safe Python value."""
    if pd.isna(value):
        return None
    number = value.item() if hasattr(value, "item") else value
    if isinstance(number, (int, float)):
        return number
    return float(number)


def analyze_csv(file_path: str | Path) -> dict[str, Any]:
    """Return a data-quality report for a CSV file.

    Raises:
        FileNotFoundError: The requested file does not exist.
        ValueError: The path is not a CSV, the file is empty, or it cannot be parsed.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if not path.is_file():
        raise ValueError("Input path must point to a file.")
    if path.suffix.lower() != ".csv":
        raise ValueError("Input file must have a .csv extension.")
    if path.stat().st_size == 0:
        raise ValueError("Input CSV is empty.")

    try:
        dataframe = pd.read_csv(path)
    except EmptyDataError as exc:
        raise ValueError("Input CSV has no readable header or data.") from exc
    except (ParserError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not parse CSV: {exc}") from exc

    missing_values = {
        str(column): int(count)
        for column, count in dataframe.isna().sum().items()
    }
    data_types = {str(column): str(dtype) for column, dtype in dataframe.dtypes.items()}

    numeric_summary: dict[str, dict[str, int | float | None]] = {}
    numeric_columns = dataframe.select_dtypes(include="number").columns
    for column in numeric_columns:
        values = dataframe[column].dropna()
        if values.empty:
            numeric_summary[str(column)] = {
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
            }
            continue
        numeric_summary[str(column)] = {
            "min": _json_number(values.min()),
            "max": _json_number(values.max()),
            "mean": _json_number(values.mean()),
            "median": _json_number(values.median()),
        }

    return {
        "file_name": path.name,
        "row_count": int(len(dataframe)),
        "column_count": int(len(dataframe.columns)),
        "duplicate_row_count": int(dataframe.duplicated().sum()),
        "missing_values_by_column": missing_values,
        "data_types_by_column": data_types,
        "numeric_summary": numeric_summary,
    }


def main() -> int:
    """Command-line entry point. Write JSON to a file or print it to stdout."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Inspect a CSV for missing values, duplicate rows, and numeric summaries."
    )
    parser.add_argument("csv_file", help="Path to the input .csv file")
    parser.add_argument(
        "--output", "-o", help="Optional path for the JSON report (default: print report)"
    )
    args = parser.parse_args()

    try:
        report = analyze_csv(args.csv_file)
    except (FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))

    rendered = json.dumps(report, indent=2, allow_nan=False)
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"Report written to {output_path}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
