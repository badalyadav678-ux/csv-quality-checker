# CSV Data Quality Checker

A small, local Python project that inspects a CSV file and creates a JSON report. It checks row/column counts, duplicate rows, missing values per column, detected data types, and min/max/mean/median for numeric columns.

## Requirements

- Python 3.10 or newer
- pip

## Setup

Create and activate a virtual environment if you normally use one, then install dependencies:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the analysis

Print a report in the terminal:

```bash
python csv_quality.py sample_data/customers.csv
```

Write a report to a JSON file:

```bash
python csv_quality.py sample_data/customers.csv --output report.json
```

## Run tests

```bash
python -m pytest -q
```

The tests cover report calculations, duplicate/missing data, missing and invalid files, zero-byte CSV files, header-only files, and JSON-safe numeric summaries.

## Scope and limitations

- Runs locally; no server, database, login, or deployment is included.
- This is a basic data-quality summary, not a full data-cleaning tool.
- Do not use it with sensitive data unless you understand where that data is stored and processed.
