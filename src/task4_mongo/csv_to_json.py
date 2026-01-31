"""
Task 4 helper: Convert Task 1 CSV -> JSON for MongoDB import.

- Input:  ../data/processed/books.csv
- Output: ../data/exports/books.json (JSON array)
          ../data/exports/books.ndjson (one JSON per line)

Why two?
- Compass can import JSON array OR NDJSON
- NDJSON is also compatible with mongoimport

Where to put this file in your repo:
    src/task4_mongo/csv_to_json.py

Run (from project root):
    python -m src.task4_mongo.csv_to_json

If you're running this standalone file:
    python csv_to_json_task4.py --csv ../data/processed/books.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def normalize_records(df: pd.DataFrame) -> list[dict]:
    """Ensure consistent types and column names for MongoDB import."""
    expected = ["title", "authors", "year", "star_rating", "price", "source_url"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}. Found: {list(df.columns)}")

    df = df.copy()

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["star_rating"] = pd.to_numeric(df["star_rating"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    if "source" not in df.columns:
        df["source"] = "manning"

    records = df.where(pd.notnull(df), None).to_dict(orient="records")
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, default="../data/processed/books.csv")
    parser.add_argument("--out_dir", type=str, default="../data/exports")
    args = parser.parse_args()

    csv_path = Path(args.csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    records = normalize_records(df)

    json_array_path = out_dir / "books.json"
    ndjson_path = out_dir / "books.ndjson"

    json_array_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    with ndjson_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("✅ Created JSON exports:")
    print(" -", json_array_path)
    print(" -", ndjson_path)
    print(f"Rows exported: {len(records)}")


if __name__ == "__main__":
    main()
