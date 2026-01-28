import os
import pandas as pd
import mysql.connector
from mysql.connector import Error

from src.common.paths import PROCESSED_DIR


def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "module15_cw1_de"),
    )


def main():
    csv_path = PROCESSED_DIR / "books.csv"
    if not csv_path.exists():
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
        # Convert pandas/NumPy scalars to plain Python types
        if pd.isna(v):
            return None
        # numpy scalar -> python scalar
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


    insert_sql = """
        INSERT INTO books_import_py (title, authors, year, star_rating, price, source_url)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    try:
        conn = get_conn()
        cur = conn.cursor()

        # Safety: clear existing data for repeatable runs
        cur.execute("TRUNCATE TABLE books_import_py;")

        cur.executemany(insert_sql, rows)
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM books_import_py;")
        count = cur.fetchone()[0]

        print(f"[OK] Inserted rows: {count}")

    except Error as e:
        raise RuntimeError(f"MySQL error: {e}") from e
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    # load .env manually (no extra dependency)
    # If you prefer python-dotenv, tell me and we’ll add it.
    if os.path.exists(".env"):
        for line in open(".env", "r", encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    main()
