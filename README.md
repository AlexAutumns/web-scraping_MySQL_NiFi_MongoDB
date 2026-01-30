# CW1 Data Engineering (CMP020X304S)  
**Web Scraping → CSV → MySQL → NiFi Export → MongoDB (Task 4 later)**

This repository is a **step-by-step** workflow for Coursework 1. It is written so that a beginner can start from zero, run the notebooks/scripts, and verify each task output.

---

## Table of Contents
- [1. What this project does](#1-what-this-project-does)
- [2. Folder structure](#2-folder-structure)
- [3. Prerequisites](#3-prerequisites)
- [4. Setup (Windows PowerShell)](#4-setup-windows-powershell)
- [5. Run with Notebooks (recommended)](#5-run-with-notebooks-recommended)
- [6. Task 1 — Web scraping (Manning → CSV)](#6-task-1--web-scraping-manning--csv)
- [7. Task 2 — MySQL database + CSV import](#7-task-2--mysql-database--csv-import)
  - [7A. UI Method (phpMyAdmin)](#7a-ui-method-phpmyadmin)
  - [7B. Code Method (repeatable)](#7b-code-method-repeatable)
  - [7C. Required SQL queries (3 columns + sort)](#7c-required-sql-queries-3-columns--sort)
  - [7D. Database schema diagram (draw.io)](#7d-database-schema-diagram-drawio)
- [8. Task 3 — Apache NiFi export (MySQL → local disk)](#8-task-3--apache-nifi-export-mysql--local-disk)
- [9. Task 4 — MongoDB integration (next)](#9-task-4--mongodb-integration-next)
- [10. End-to-end testing checklist](#10-end-to-end-testing-checklist)
- [11. Troubleshooting](#11-troubleshooting)

---

## 1. What this project does

Coursework tasks (as required in the spec):

- **Task 1 (25%)**: Scrape at least **15 Data Engineering books** from an e-commerce site (we use **Manning**) and save the results to CSV.
- **Task 2 (25%)**: Create a **MySQL database**, import the CSV, and run SQL queries (including selecting 3 columns and sorting).
- **Task 3 (25%)**: Use **Apache NiFi** to extract data from MySQL and save it locally in a structured format (JSON/CSV).
- **Task 4 (25%)**: Convert CSV → JSON, import into **MongoDB**, run MongoDB queries, and compare query execution time with MySQL.

> **Note about `star_rating`:** On Manning listings, the rating display is often missing.  
> If a rating exists, it is commonly shown as a **review count in parentheses** like `(4)`.  
> Therefore `star_rating` can be **NULL** and that is expected.

---

## 2. Folder structure

```
.
├─ data/
│  ├─ raw/                      # intermediate scrape outputs
│  └─ processed/                # final CW1 CSV output (Task 1)
├─ notebooks/
│  ├─ 01_task1_web_scrape_manning.ipynb
│  └─ 02_task2_mysql_create_import_query.ipynb
├─ nifi/                        # NiFi notes/templates (Task 3)
├─ scripts/                     # optional .bat runners (Windows)
├─ src/
│  ├─ task1_scrape/             # Manning scraper + runner
│  ├─ task2_sql/                # DB schema + CSV import + runner
│  └─ task4_mongo/              # placeholders (will be implemented in Task 4)
├─ requirements.txt
└─ README.md
```

---

## 3. Prerequisites

### 3.1 Python
Recommended: **Python 3.11+** (3.13 is fine).

Check:
```powershell
python --version
py --version
```

### 3.2 MySQL + phpMyAdmin (local)
Recommended for this CW setup: **XAMPP**.
- Start **Apache**
- Start **MySQL**
- Open phpMyAdmin: `http://localhost/phpmyadmin`

### 3.3 Apache NiFi (Task 3)
- NiFi **2.6** installed and running
- MySQL JDBC driver (MySQL Connector/J JAR)

### 3.4 MongoDB (Task 4)
- MongoDB Community Server (local) or MongoDB Atlas
- MongoDB Compass is optional (GUI)

---

## 4. Setup (Windows PowerShell)

From the project root folder:

### 4.1 Create & activate a virtual environment
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4.2 Upgrade pip + install dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4.3 (Recommended) Register the venv as a Jupyter kernel
This makes your notebook run with the same packages you installed:
```powershell
python -m ipykernel install --user --name cw1-de --display-name "CW1 Data Engineering (.venv)"
```

### 4.4 Start Jupyter
```powershell
jupyter lab
```
Open the `notebooks/` folder and select kernel:
**Kernel → Change Kernel → CW1 Data Engineering (.venv)**

---

## 5. Run with Notebooks (recommended)

Open and run these in order:

1. `notebooks/01_task1_web_scrape_manning.ipynb`  
2. `notebooks/02_task2_mysql_create_import_query.ipynb`

Each notebook is designed to mirror what the `.py` scripts do, but in a “coursework-friendly” format with markdown titles and clear output cells.

---

## 6. Task 1 — Web scraping (Manning → CSV)

### Option A (Notebook)
Run:
- `notebooks/01_task1_web_scrape_manning.ipynb`

### Option B (Python script)
Run:
```powershell
python -m src.task1_scrape.manning_run
```

### Output files
After Task 1, you should have:
- `data/raw/books_manning_raw.csv`
- `data/processed/books.csv` ✅ (this is the CSV used in Task 2)

### Minimum rows check (quick)
Open the CSV in Excel OR run:
```powershell
python -c "import pandas as pd; df=pd.read_csv('data/processed/books.csv'); print(df.shape); print(df.head(3))"
```
You need **at least 15 rows**.

### Where URLs/sources are defined
- `src/task1_scrape/sources.py`

---

## 7. Task 2 — MySQL database + CSV import

You have two valid approaches (both are acceptable).  
**The code method is recommended** because it is repeatable and avoids phpMyAdmin CSV import quirks.

### Start services first
Open **XAMPP Control Panel**:
- Start **Apache**
- Start **MySQL**

---

## 7A. UI Method (phpMyAdmin)

This section is fully “UI-first” (create DB in phpMyAdmin, create table using the SQL tab, and import CSV in the Import tab).

### Step A1 — Create a database using the UI
1. Go to phpMyAdmin: `http://localhost/phpmyadmin`
2. Click **New**
3. Database name: `module15_cw1_de`
4. Collation: keep default (e.g., `utf8mb4_general_ci`)
5. Click **Create**

### Step A2 — Create a table for UI import (SQL tab)
Select your database (`module15_cw1_de`) → click **SQL** → paste & run:

```sql
DROP TABLE IF EXISTS books_import_ui;

CREATE TABLE books_import_ui (
  title VARCHAR(255) NOT NULL,
  authors TEXT NOT NULL,
  year INT NOT NULL,
  star_rating FLOAT NULL,
  price DECIMAL(10,2) NOT NULL,
  source_url TEXT NOT NULL
);
```

### Step A3 — Import the CSV using the phpMyAdmin UI
1. Click table: `books_import_ui`
2. Click **Import**
3. Choose file: `data/processed/books.csv`
4. Format: **CSV**
5. Typical settings (may vary by phpMyAdmin version):
   - Column separator: `,`
   - Enclosure: `"`
   - Escape: `\`
   - If there is an option: **“The first line of the file contains the table column names”** → enable it
6. Click **Import**

### Step A4 — Verify the import
Run in **SQL** tab:

```sql
SELECT COUNT(*) AS row_count
FROM books_import_ui;
```

---

## 7B. Code Method (repeatable)

This method uses Python to:
- connect to MySQL
- create the database/table if needed
- import the CSV reliably

### Step B1 — Create a `.env` file (project root)
Create a file named `.env` in the project root (this should NOT be committed to git):

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=module15_cw1_de
```

> In XAMPP, the default is usually `root` with an empty password.  
> If you changed it, set `DB_PASSWORD` accordingly.

### Step B2 — Run Task 2 from the notebook
Run:
- `notebooks/02_task2_mysql_create_import_query.ipynb`

### Step B3 — OR run Task 2 from the script
**Primary (code-created) database + import:**
```powershell
python -m src.task2_sql.run_task2_all
```

This creates/imports into:
- DB (default): `module15_cw1_de_py`
- Table (default): `books_import_py`

**Also import into your UI DB from `.env`:**
```powershell
python -m src.task2_sql.run_task2_all --also-ui
```

**Change database/table names (optional):**
```powershell
python -m src.task2_sql.run_task2_all --primary-db module15_cw1_de_py --table books_import_py
python -m src.task2_sql.run_task2_all --also-ui --ui-db module15_cw1_de --table books_import_py
```

---

## 7C. Required SQL queries (3 columns + sort)

The coursework requires:  
✅ “Extract only 3 columns and sort the table based on any column.”

Run these in phpMyAdmin → **SQL** tab (choose the correct table name):

### 1) Count rows
```sql
SELECT COUNT(*) AS row_count
FROM books_import_py;
```

### 2) Select 3 columns + sort by price (descending)
```sql
SELECT title, authors, price
FROM books_import_py
ORDER BY price DESC;
```

### 3) Select 3 columns + sort by year then price
```sql
SELECT title, year, price
FROM books_import_py
ORDER BY year DESC, price DESC;
```

> If you used the UI table instead, replace `books_import_py` with `books_import_ui`.

---

## 7D. Database schema diagram (draw.io)

The spec asks you to draw the table structure in **draw.io** (diagrams.net).

Suggested schema (single table):

**Table: `books_import_py` (or `books_import_ui`)**
- title (VARCHAR)
- authors (TEXT)
- year (INT)
- star_rating (FLOAT, nullable)
- price (DECIMAL(10,2))
- source_url (TEXT)

In draw.io:
1. Create a new diagram → choose **Entity Relation** or **Database** shapes
2. Add one entity/table box
3. Add attributes as above
4. Export as PNG/PDF for your report

---

## 8. Task 3 — Apache NiFi export (MySQL → local disk)

Goal: extract data stored in MySQL and save it to local disk as **JSON** (recommended) or CSV.

### 8.1 Prerequisites checklist
- NiFi **2.6** installed and running
- MySQL is running (XAMPP)
- MySQL Connector/J JAR copied into: `NIFI_HOME/lib/`
- Restart NiFi after adding the JAR

### 8.2 Suggested NiFi flow (simple + coursework-friendly)

**Processors:**
`ExecuteSQLRecord → UpdateAttribute → PutFile`

#### Step 1 — Create a Process Group
- Name: `Task 3 – MySQL to JSON Extract`

#### Step 2 — Add processors inside the group
- ExecuteSQLRecord
- UpdateAttribute
- PutFile

#### Step 3 — Configure ExecuteSQLRecord
Key properties:
- **Database Connection Pooling Service**: create **DBCPConnectionPool**
- **SQL Select Query**: choose the table you imported into, e.g.

```sql
SELECT * FROM books_import_py;
```

- **Record Writer**: create **JsonRecordSetWriter**  
  Suggested writer settings:
  - Pretty Print JSON: `true`
  - Output Records Per FlowFile: `Single JSON Array`
  - Character Set: `UTF-8`

#### Step 4 — Configure DBCPConnectionPool (Controller Service)
Typical values:
- Database Connection URL: `jdbc:mysql://localhost:3306/module15_cw1_de_py`
- Driver Class Name: `com.mysql.cj.jdbc.Driver`
- Driver Location(s): path to the JAR (example) `C:\nifi\lib\mysql-connector-j-8.1.0.jar`
- Database User: `root`
- Password: (your MySQL password)

Enable the service.

#### Step 5 — Configure UpdateAttribute
Add attribute:
- `filename` = `books_${now():format("yyyyMMdd_HHmmss")}.json`

#### Step 6 — Configure PutFile
- Directory: create a folder named (example)  
  `C:\Data Engineering extract`
- Create Missing Directories: `true`
- Conflict Resolution Strategy: `replace`

#### Step 7 — Run Once + verify output
1. Start processors in order: ExecuteSQLRecord → UpdateAttribute → PutFile
2. Right-click **ExecuteSQLRecord** → **Run Once**
3. Check your output folder for a JSON file like:  
   `books_20250130_162201.json`

**Video tip (Task 3 submission):**
- Record your screen + keep your camera ON (as required)
- Show: NiFi UI, processor configs, “Run Once”, and the output file opening

---

## 9. Task 4 — MongoDB integration (next)

Planned steps:
1. Convert `data/processed/books.csv` → `books.json`
2. Import JSON into MongoDB
3. Query MongoDB (filter by price/year, sort, etc.)
4. Compare query execution time vs MySQL (simple benchmark)

> Note: `src/task4_mongo/` currently contains placeholders and will be implemented in Task 4.

---

## 10. End-to-end testing checklist

Use this to test from scratch (the README is designed to be your test plan):

1. Create `.venv` and install requirements  
2. Start XAMPP (Apache + MySQL)  
3. Run **Task 1 notebook** → confirm `data/processed/books.csv` exists and has ≥ 15 rows  
4. Create DB in phpMyAdmin (UI) OR create `.env` (code method)  
5. Run **Task 2 notebook** → confirm table exists and has rows  
6. Run SQL verification queries (3 columns + sorting)  
7. (Later) Build NiFi flow and export JSON to local disk  
8. (Later) Convert CSV → JSON and import to MongoDB; query + compare execution times  

---

## 11. Troubleshooting

### Jupyter kernel missing
Re-run:
```powershell
python -m ipykernel install --user --name cw1-de --display-name "CW1 Data Engineering (.venv)"
```

### MySQL connection fails (Access denied)
- Ensure MySQL is running in XAMPP
- Check `.env` values (host/port/user/password)
- In phpMyAdmin, verify the user credentials you expect

### CSV import issues in phpMyAdmin
If UI import fails or columns misalign, use the **code method**:
```powershell
python -m src.task2_sql.run_task2_all --also-ui
```

### Task 1 returns fewer than 15 rows
- Re-run Task 1 (site pages can change)
- Verify your internet connection
- Check `src/task1_scrape/sources.py` if you changed URLs

---

### Academic integrity reminder
Keep your code well-commented and screenshot your outputs (Task 1 & 2).  
If you borrow code/ideas, reference the source in your report.
