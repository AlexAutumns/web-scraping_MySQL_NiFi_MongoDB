import os
import argparse

from src.task2_sql.create_schema import ensure_schema
from src.task2_sql.import_csv import import_csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="module15_cw1_de_py", help="Database name to create/use")
    parser.add_argument("--table", default="books_import_py", help="Table name to create/use")
    args = parser.parse_args()

    print("=== TASK 2 END-TO-END ===")
    print(f"[INFO] Target DB: {args.db}")
    print(f"[INFO] Target table: {args.table}")

    print("[STEP 1] Create database + table (code)")
    ensure_schema(args.db, args.table)

    print("[STEP 2] Import CSV into table")
    count = import_csv(db_name=args.db, table_name=args.table)

    print("[DONE] Task 2 completed")
    print(f"[RESULT] Inserted rows: {count}")


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
