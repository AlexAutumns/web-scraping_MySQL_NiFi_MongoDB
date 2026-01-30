import os
import re
import mysql.connector
from mysql.connector import Error

IDENT_RE = re.compile(r"^[A-Za-z0-9_]+$")


def _validate_ident(name: str, kind: str) -> str:
    if not IDENT_RE.match(name):
        raise ValueError(
            f"Invalid {kind} '{name}'. Use only letters, numbers, and underscore."
        )
    return name


def get_server_conn():
    """Connect to MySQL server WITHOUT selecting a database."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def ensure_database(db_name: str) -> None:
    db_name = _validate_ident(db_name, "database name")

    sql = f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"

    try:
        conn = get_server_conn()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        print(f"[DB] ensured database exists: {db_name}")
    except Error as e:
        raise RuntimeError(f"MySQL error while creating database: {e}") from e
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass


def ensure_table(db_name: str, table_name: str) -> None:
    db_name = _validate_ident(db_name, "database name")
    table_name = _validate_ident(table_name, "table name")

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS `{db_name}`.`{table_name}` (
      title VARCHAR(255) NOT NULL,
      authors TEXT NOT NULL,
      year INT NOT NULL,
      star_rating FLOAT NULL,
      price DECIMAL(10,2) NOT NULL,
      source_url TEXT NOT NULL
    );
    """

    try:
        conn = get_server_conn()
        cur = conn.cursor()
        cur.execute(create_table_sql)
        conn.commit()
        print(f"[DB] ensured table exists: {db_name}.{table_name}")
    except Error as e:
        raise RuntimeError(f"MySQL error while creating table: {e}") from e
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass


def ensure_schema(db_name: str, table_name: str) -> None:
    ensure_database(db_name)
    ensure_table(db_name, table_name)


if __name__ == "__main__":
    # Manual .env load (same pattern you're using elsewhere)
    if os.path.exists(".env"):
        for line in open(".env", "r", encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

    # Defaults
    ensure_schema(
        db_name=os.getenv("DB_NAME", "module15_cw1_de_py"),
        table_name=os.getenv("DB_TABLE", "books_import_py"),
    )
