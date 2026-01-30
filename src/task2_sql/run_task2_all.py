import os
import argparse

from src.task2_sql.create_schema import ensure_schema
from src.task2_sql.import_csv import import_csv


def load_env():
    if os.path.exists(".env"):
        for line in open(".env", "r", encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main():
    parser = argparse.ArgumentParser(description="Task 2: create schema + import CSV (one or more DBs)")
    parser.add_argument("--table", default="books_import_py", help="Table name")
    parser.add_argument(
        "--primary-db",
        default="module15_cw1_de_py",
        help="Primary DB (code-created recommended)",
    )
    parser.add_argument(
        "--also-ui",
        action="store_true",
        help="Also import into the UI DB from .env (DB_NAME) or default module15_cw1_de",
    )
    parser.add_argument(
        "--ui-db",
        default=None,
        help="Override UI DB name (if not set, uses DB_NAME from .env or module15_cw1_de)",
    )
    args = parser.parse_args()

    load_env()

    table = args.table

    print("=== TASK 2 RUNNER ===")
    print(f"[INFO] Table: {table}")

    # --- Primary DB (code-created) ---
    primary_db = args.primary_db
    print(f"\n[PRIMARY] {primary_db}")
    print("[STEP 1] Ensure schema (DB + table)")
    ensure_schema(primary_db, table)

    print("[STEP 2] Import CSV")
    import_csv(db_name=primary_db, table_name=table)

    # --- Optional UI DB sync ---
    if args.also_ui:
        ui_db = args.ui_db or os.getenv("DB_NAME", "module15_cw1_de")
        print(f"\n[UI] {ui_db}")
        print("[STEP 1] Ensure table exists (safe even if DB already exists)")
        ensure_schema(ui_db, table)

        print("[STEP 2] Import CSV")
        import_csv(db_name=ui_db, table_name=table)

    print("\n[DONE] Task 2 runner finished.")


if __name__ == "__main__":
    main()
