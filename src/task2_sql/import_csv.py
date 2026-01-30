import os
import re
import argparse
import pandas as pd
import mysql.connector
from mysql.connector import Error

from src.common.paths import PROCESSED_DIR

IDENT_RE = re.compile(r"^[A-Za-z0-9_]+$")


def _validate_ident(name: str, kind: str) -> str:
    if not IDENT_RE.match(name):
        raise ValueError(f"Invalid {kind} '{name}'. Use only letters, numbers, and underscore.")
    return name


def get_conn(db_name: str):
    db_name = _validate_ident(db_name, "database name")
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=db_name,
    )


def import_csv(db_name: str, table_name: str, csv_path: str | None = None) -> int:
    table_name = _validate_ident(table_name, "table name")

    if csv_path is None:
        csv_path = str(PROCESSED_DIR / "books.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    required_cols = ["title", "authors", "year", "star_rating", "price", "source_url"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

    # Clean types
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["star_rating"] = pd.to_numeric(df["star_rating"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Drop rows that can’t be inserted
    df = df.dropna(subset=["title", "authors", "year", "price", "source_url"]).copy()

    def to_py(v):
        if pd.isna(v):
            return None
        if hasattr(v, "item"):
            try:
                return v.item()
            except Exception:
                pass
        return v

    rows = [
        tuple(to_py(v) for v in row)
        for row in df[required_cols].itertuples(index=False, name=None)
    ]

    insert_sql = f"""
        INSERT INTO `{table_name}` (title, authors, year, star_rating, price, source_url)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    try:
        conn = get_conn(db_name)
        cur = conn.cursor()

        cur.execute(f"TRUNCATE TABLE `{table_name}`;")
        cur.executemany(insert_sql, rows)
        conn.commit()

        cur.execute(f"SELECT COUNT(*) FROM `{table_name}`;")
        count = cur.fetchone()[0]
        print(f"[OK] Inserted rows into {db_name}.{table_name}: {count}")
        return int(count)

    except Error as e:
        raise RuntimeError(f"MySQL error: {e}") from e
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=os.getenv("DB_NAME", "module15_cw1_de"), help="Database name")
    parser.add_argument("--table", default=os.getenv("DB_TABLE", "books_import_py"), help="Table name")
    parser.add_argument("--csv", default=None, help="Path to CSV (defaults to data/processed/books.csv)")
    args = parser.parse_args()

    import_csv(db_name=args.db, table_name=args.table, csv_path=args.csv)


if __name__ == "__main__":
    # load .env manually
    if os.path.exists(".env"):
        for line in open(".env", "r", encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    main()
