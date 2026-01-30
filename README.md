# CW1 Data Engineering — Web Scraping → MySQL → (NiFi) → (MongoDB)

This repository contains the working **Python-first** implementation for **CW1**:

- **Task 1:** Scrape a minimum of **15** Data Engineering book records from **Manning** and save as CSV.
- **Task 2:** Create a SQL database **via code**, create table(s), and import the CSV into MySQL (XAMPP/phpMyAdmin compatible).
- **Task 3 (next):** Export data from MySQL to local disk in a structured format using Apache NiFi.
- **Task 4 (next):** Convert CSV → JSON, load into MongoDB, then compare MongoDB vs SQL.

> **Note on `star_rating`:** On Manning catalog pages, the value we capture is typically a **review count shown in parentheses** like `(4)`.  
> Many books have **no rating display**, so `star_rating` can be `NULL` — that’s expected.

---

## Project structure

```
.
├─ data/
│  ├─ raw/                # intermediate scrape outputs
│  └─ processed/          # final CW1 outputs (Task 1 CSV)
├─ nifi/                  # NiFi notes + (later) templates/exports
├─ src/
│  ├─ common/             # shared paths/helpers (some placeholders)
│  ├─ task1_scrape/       # Manning scraper + runners
│  ├─ task2_sql/          # DB creation + CSV import + runners
│  └─ task4_mongo/        # placeholders for Task 4 (to be implemented)
├─ requirements.txt
└─ .gitignore
```

---

## Prerequisites

### 1) Python
Recommended: **Python 3.11+** (you’re using 3.13 which is fine).

Check:
```powershell
python --version
python -c "import sys; print(sys.executable)"
```

### 2) MySQL (local)
Recommended for this coursework setup: **XAMPP** (MySQL + phpMyAdmin).

Start via **XAMPP Control Panel**:
- Start **Apache**
- Start **MySQL**

Open phpMyAdmin:
- http://localhost/phpmyadmin

---

## Setup (Windows PowerShell)

From project root:

### 1) Create & activate venv
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configuration (.env)

Create a `.env` file in the project root (this is ignored by git):

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=module15_cw1_de
```

- In XAMPP, the default user is often `root` with empty password.
- If you set a password, update `DB_PASSWORD`.

---

## Task 1 — Web scraping (Manning → CSV)

Run:
```powershell
python -m src.task1_scrape.manning_run
```

Outputs:
- `data/raw/books_manning_raw.csv`
- `data/processed/books.csv`  ✅ (this is the file used by Task 2)

### Where the sources are defined
Edit:
- `src/task1_scrape/sources.py`

### Debugging Task 1 (optional)
In:
- `src/task1_scrape/manning_scraper.py`

Set:
```python
DEBUG = True
```

Then rerun the scraper to print a readable “row debug” block for each parsed listing.

---

## Task 2 — MySQL database + import CSV

### Option A: UI import (phpMyAdmin)
You *can* import the CSV manually, but phpMyAdmin CSV import options differ by version and can be inconsistent.

If you still want the UI method:
1. Create a database in phpMyAdmin (example): `module15_cw1_de`
2. Create a table (example name): `books_import_ui`
3. Import `data/processed/books.csv`

### Option B (recommended): Code-driven DB creation + CSV import
This is the most repeatable approach and matches the “database via code” requirement.

#### 1) Create schema + import into code-created DB
This creates:
- DB: `module15_cw1_de_py` (default)
- Table: `books_import_py` (default)

```powershell
python -m src.task2_sql.run_task2_all
```

#### 2) Also import into your UI DB (optional)
This imports the same CSV into the DB set in `.env` (or whatever you pass via `--ui-db`):

```powershell
python -m src.task2_sql.run_task2_all --also-ui
```

#### Useful flags
```powershell
# choose a different primary DB name
python -m src.task2_sql.run_task2_all --primary-db module15_cw1_de_py

# import into a specific UI DB name (override .env)
python -m src.task2_sql.run_task2_all --also-ui --ui-db module15_cw1_de
```

### Quick SQL checks (run in phpMyAdmin → SQL tab)
```sql
SELECT COUNT(*) AS row_count FROM books_import_py;

SELECT title, authors, price
FROM books_import_py
ORDER BY price DESC;

SELECT title, year, price
FROM books_import_py
ORDER BY year DESC, price DESC;
```

---

## Task 3 — Apache NiFi export (next)

Goal:
- Extract data stored in MySQL and write to local disk in a structured format (e.g., CSV/JSON/Avro/Parquet depending on your spec/tools)

Planned output folder suggestion:
- `data/exports/`

We will add:
- NiFi installation steps
- NiFi template/process group configuration
- Driver setup (JDBC)
- Example flow: QueryDatabaseTableRecord → ConvertRecord → PutFile

---

## Task 4 — MongoDB JSON + comparison (next)

Planned steps:
1. Convert the final CSV to JSON (array of documents)
2. Import JSON to MongoDB
3. Benchmark / compare SQL vs MongoDB for simple queries (counts, filters, sorts, etc.)

---

## Notebooks (.ipynb) deliverables

The project currently focuses on **working `.py` code first**.

Suggested notebooks location (create later):
```
notebooks/
├─ Task1_Scrape_Manning.ipynb
└─ Task2_SQL_Create_Import.ipynb
```

Because you already installed Jupyter + ipykernel, you can create notebooks and select your kernel:
- `CW1 Data Engineering (.venv)` (your installed kernel)

---

## Troubleshooting

### “403 Forbidden” on Packt
Packt may block local scraping (works sometimes in Colab). Use the **Manning** scraper as your main source.

### Ratings are NULL
This is normal for books with no rating display.
If you want to inspect parsing per row, enable:
```python
DEBUG = True
```
in `manning_scraper.py`.

### “Python type numpy.int64 cannot be converted” (MySQL import)
Already handled in `import_csv.py` by converting numpy scalars to native Python types before insert.

---

## License / usage
Educational coursework repository (CW1). Keep your `.env` private (it is ignored by git).
