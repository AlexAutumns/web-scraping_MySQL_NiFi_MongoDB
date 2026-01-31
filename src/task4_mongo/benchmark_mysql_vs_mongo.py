"""
Task 4 helper: Benchmark query execution time - MySQL vs MongoDB.

This is a simple benchmark for coursework evidence.
It runs the *same kind of query* in both databases (filter + sort) and measures elapsed time.

Assumptions:
- MySQL table: module15_cw1_de_py.books_import_py
- MongoDB: localhost:27017, database: cw1_de, collection: books

You can change these via arguments.

Prereqs:
    pip install pymongo mysql-connector-python pandas

Where to put this file in your repo:
    src/task4_mongo/benchmark.py

Run (from project root):
    python -m src.task4_mongo.benchmark --min_price 30

If you're running this standalone file:
    python benchmark_task4_mysql_vs_mongo.py --min_price 30
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import mysql.connector
from pymongo import MongoClient


def load_env_from_project_root() -> None:
    """Walk upward to find and load a .env file if present."""
    start = Path.cwd().resolve()
    for parent in [start, *start.parents]:
        env_path = parent / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
            return


def mysql_query_benchmark(host: str, port: int, user: str, password: str, db: str, table: str, min_price: float) -> tuple[float, int]:
    """Filter + sort query benchmark in MySQL."""
    t0 = time.perf_counter()
    conn = mysql.connector.connect(host=host, port=port, user=user, password=password, database=db)
    cur = conn.cursor()

    sql = f"""
    SELECT title, year, price
    FROM {table}
    WHERE price >= %s
    ORDER BY price DESC;
    """
    cur.execute(sql, (min_price,))
    rows = cur.fetchall()

    cur.close()
    conn.close()
    t1 = time.perf_counter()
    return (t1 - t0), len(rows)


def mongo_query_benchmark(uri: str, db: str, collection: str, min_price: float) -> tuple[float, int]:
    """Filter + sort query benchmark in MongoDB."""
    t0 = time.perf_counter()
    client = MongoClient(uri)
    coll = client[db][collection]

    cursor = coll.find(
        {"price": {"$gte": min_price}},
        {"_id": 0, "title": 1, "year": 1, "price": 1},
    ).sort("price", -1)

    rows = list(cursor)
    client.close()
    t1 = time.perf_counter()
    return (t1 - t0), len(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min_price", type=float, default=30.0)

    parser.add_argument("--mysql_db", type=str, default="module15_cw1_de_py")
    parser.add_argument("--mysql_table", type=str, default="books_import_py")

    parser.add_argument("--mongo_uri", type=str, default="mongodb://localhost:27017")
    parser.add_argument("--mongo_db", type=str, default="cw1_de")
    parser.add_argument("--mongo_collection", type=str, default="books")
    args = parser.parse_args()

    load_env_from_project_root()

    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    print("=== Benchmark settings ===")
    print("MySQL:", f"{DB_HOST}:{DB_PORT}", "db:", args.mysql_db, "table:", args.mysql_table)
    print("Mongo:", args.mongo_uri, "db:", args.mongo_db, "collection:", args.mongo_collection)
    print("Query: price >=", args.min_price)
    print()

    mysql_time, mysql_count = mysql_query_benchmark(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
        db=args.mysql_db, table=args.mysql_table, min_price=args.min_price
    )
    mongo_time, mongo_count = mongo_query_benchmark(
        uri=args.mongo_uri, db=args.mongo_db, collection=args.mongo_collection, min_price=args.min_price
    )

    print("=== Results ===")
    print(f"MySQL  -> {mysql_time:.6f} sec | rows: {mysql_count}")
    print(f"MongoDB-> {mongo_time:.6f} sec | rows: {mongo_count}")
    print()
    if mysql_count != mongo_count:
        print("⚠️ Row counts differ. That can happen if one DB has different data loaded.")
    else:
        print("✅ Row counts match. Good for a fair comparison.")


if __name__ == "__main__":
    main()
