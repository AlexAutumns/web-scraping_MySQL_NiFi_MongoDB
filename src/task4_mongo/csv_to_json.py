"""
Task 4: Convert Task 1 CSV -> JSON for MongoDB Compass import (robust paths).

Works regardless of where you run it from (project root, src/, VS Code, etc.).

Expected project structure:
  Project/
    data/processed/books.csv
    data/exports/            (will be created)
    src/task4_mongo/csv_to_json.py   (this file)

Outputs:
  data/exports/books.json    (JSON array)
  data/exports/books.ndjson  (NDJSON, one JSON object per line)

Run (recommended):
  # from project root
  python -m src.task4_mongo.csv_to_json

Or:
  python src/task4_mongo/csv_to_json.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def find_project_root(start: Path) -> Path:
    """
    Find the project root by walking upwards until we see a 'data/processed' folder
    or a README.md. This avoids fragile relative paths.
    """
    start = start.resolve()
    for p in [start, *start.parents]:
        if (p / "data" / "processed").exists():
            return p
        if (p / "README.md").exists() and (p / "data").exists():
            return p
    # Fallback to the folder containing this script (2 levels up: src/task4_mongo -> src -> project root)
    return Path(__file__).resolve().parents[2]


def normalize_records(df: pd.DataFrame) -> list[dict]:
    """Ensure consistent types and column names for MongoDB import."""
    expected = ["title", "authors", "year", "star_rating", "price", "source_url"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}. Found: {list(df.columns)}")

    df = df.copy()

    # clean numeric types
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["star_rating"] = pd.to_numeric(df["star_rating"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # add a simple source label (optional but useful)
    if "source" not in df.columns:
        df["source"] = "manning"

    # NaN/NA -> None so JSON becomes null
    return df.where(pd.notnull(df), None).to_dict(orient="records")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, default=None, help="Path to books.csv (optional)")
    parser.add_argument("--out_dir", type=str, default=None, help="Output directory (optional)")
    args = parser.parse_args()

    project_root = find_project_root(Path.cwd())

    csv_path = Path(args.csv).resolve() if args.csv else (project_root / "data" / "processed" / "books.csv")
    out_dir = Path(args.out_dir).resolve() if args.out_dir else (project_root / "data" / "exports")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        raise FileNotFoundError(
            "CSV not found.\n"
            f"Tried: {csv_path}\n"
            "Expected it at: <project_root>/data/processed/books.csv\n"
            "Fix: either create the CSV by running Task 1, or run with --csv <path>"
        )

    df = pd.read_csv(csv_path)
    records = normalize_records(df)

    json_array_path = out_dir / "books.json"
    ndjson_path = out_dir / "books.ndjson"

    json_array_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    with ndjson_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("✅ CSV -> JSON export complete")
    print("Project root:", project_root)
    print("Input CSV:", csv_path)
    print("Outputs:")
    print(" -", json_array_path)
    print(" -", ndjson_path)
    print("Rows exported:", len(records))


if __name__ == "__main__":
    main()
