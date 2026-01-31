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
  - [8.1 What you will build](#81-what-you-will-build)
  - [8.2 NiFi installation (Windows)](#82-nifi-installation-windows)
  - [8.3 Add MySQL JDBC driver (Connector/J)](#83-add-mysql-jdbc-driver-connectorj)
  - [8.4 Create the NiFi flow (beginner step-by-step)](#84-create-the-nifi-flow-beginner-step-by-step)
  - [8.5 Run it once (or stop it when you need to)](#85-run-it-once-or-stop-it-when-you-need-to)
  - [8.6 What to record for your Task 3 video](#86-what-to-record-for-your-task-3-video)
  - [8.7 Common errors and fixes](#87-common-errors-and-fixes)
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
│  ├─ processed/                # final CW1 CSV output (Task 1)
│  └─ exports/                  # JSON exports for MongoDB (Task 4)
├─ notebooks/
│  ├─ 01_task1_web_scrape_manning.ipynb
│  ├─ 02_task2_mysql_create_import_query.ipynb
│  └─ 03_task4_mongodb_compass_and_benchmark.ipynb
├─ nifi/                        # NiFi output folder for Task 3 (JSON exports)
├─ scripts/                     # optional .bat runners (Windows)
├─ src/
│  ├─ task1_scrape/             # Manning scraper + runner
│  ├─ task2_sql/                # DB schema + CSV import + runner
│  └─ task4_mongo/              # Task 4 helpers (CSV→JSON, benchmark)
│     ├─ csv_to_json.py
│     └─ benchmark.py
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
- Apache NiFi **2.7.x** (this project tested with **2.7.2**)
- **Java 21** recommended for NiFi 2.x
- MySQL JDBC driver (MySQL Connector/J `.jar`)

### 3.4 MongoDB (Task 4)
- MongoDB Community Server (local)
- MongoDB Compass (GUI) — **we use Compass for all MongoDB steps**

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

> For Task 4, ensure `pymongo` is installed:
> ```powershell
> pip install pymongo
> ```

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

> **Notebook path tip:** In VS Code/Jupyter, the working directory is often `notebooks/`.  
> That’s why notebook paths use `../data/...` and `.env` should be loaded from `../.env`.

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
5. Typical settings:
   - Column separator: `,`
   - Enclosure: `"`
   - Escape: `\`
   - Enable: **first line contains column names** (if available)
6. Click **Import**

### Step A4 — Verify the import
```sql
SELECT COUNT(*) AS row_count
FROM books_import_ui;
```

---

## 7B. Code Method (repeatable)

### Step B1 — Create a `.env` file (project root)
Create a file named `.env` in the project root (this should NOT be committed to git):

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=module15_cw1_de
```

### Step B2 — Run Task 2 from the notebook
Run:
- `notebooks/02_task2_mysql_create_import_query.ipynb`

### Step B3 — OR run Task 2 from the script
```powershell
python -m src.task2_sql.run_task2_all
```

This creates/imports into:
- DB (default): `module15_cw1_de_py`
- Table (default): `books_import_py`

---

## 7C. Required SQL queries (3 columns + sort)

The coursework requires:  
✅ “Extract only 3 columns and sort the table based on any column.”

Examples:

```sql
SELECT COUNT(*) AS row_count
FROM books_import_py;
```

```sql
SELECT title, authors, price
FROM books_import_py
ORDER BY price DESC;
```

```sql
SELECT title, year, price
FROM books_import_py
ORDER BY year DESC, price DESC;
```

---

## 7D. Database schema diagram (draw.io)

Suggested schema (single table):

**Table: `books_import_py` (or `books_import_ui`)**
- title (VARCHAR)
- authors (TEXT)
- year (INT)
- star_rating (FLOAT, nullable)
- price (DECIMAL(10,2))
- source_url (TEXT)

---

## 8. Task 3 — Apache NiFi export (MySQL → local disk)

### 8.1 What you will build

Goal: extract the data stored in MySQL and export it to a **local JSON file**.

We will build this simple flow (beginner-friendly and coursework-friendly):

**ExecuteSQLRecord → UpdateAttribute → PutFile**

- **ExecuteSQLRecord**: runs `SELECT * FROM books_import_py;`
- **UpdateAttribute**: sets `filename` to a timestamped value
- **PutFile**: writes the JSON file into your repo folder `./nifi/`

---

### 8.2 NiFi installation (Windows)

#### Step 1 — Install Java (important)
NiFi 2.x works best with **Java 21**.

Confirm your Java version:
```powershell
java -version
```

#### Step 2 — Extract NiFi
Extract NiFi somewhere simple, example:
```
<NIFI_HOME>\nifi-2.7.2\
```

#### Step 3 — Start NiFi (Windows)
Open a terminal in:
```
<NIFI_HOME>\nifi-2.7.2\bin
```

Start:
```bat
nifi.cmd start
```

Check status:
```bat
nifi.cmd status
```

Stop:
```bat
nifi.cmd stop
```

#### Step 4 — Open the NiFi UI
Open:
```
https://localhost:8443/nifi
```

**“Not Secure” warning is normal** (self-signed certificate on localhost).  
Click **Advanced → Proceed**.

#### Step 5 — Login credentials
On first run NiFi generates credentials.  
Open the log file and search for the generated username/password:
```
<NIFI_HOME>\nifi-2.7.2\logs\nifi-app.log
```

> **Antivirus note (Avast / IDP.Generic):** Some antivirus tools flag NiFi as a generic risk because it runs a local server.  
> If you downloaded NiFi from Apache and it gets quarantined, restore it and add an exception for your NiFi folder.

---

### 8.3 Add MySQL JDBC driver (Connector/J)

NiFi needs the MySQL JDBC `.jar` to connect to MySQL.

#### Step 1 — Download MySQL Connector/J jar
Example jar name:
- `mysql-connector-j-9.6.0.jar`

#### Step 2 — Copy jar into NiFi lib folder
Copy the jar into:
```
<NIFI_HOME>\nifi\nifi-2.7.2\lib\
```

Example full path:
```
<NIFI_HOME>\nifi\nifi-2.7.2\lib\mysql-connector-j-9.6.0.jar
```

#### Step 3 — Restart NiFi
After adding the jar, restart NiFi:
```bat
nifi.cmd stop
nifi.cmd start
```

---

### 8.4 Create the NiFi flow (beginner step-by-step)

#### Step 1 — Confirm MySQL is running
Start MySQL in XAMPP and verify your table exists, e.g. in phpMyAdmin:
```sql
SELECT COUNT(*) FROM books_import_py;
```

#### Step 2 — Create a Process Group
On the NiFi canvas:
- Drag **Process Group** onto the canvas
- Name: `CW1 Task3 - MySQL Export`
- Double-click it to go inside

#### Step 3 — Add processors (drag-and-drop)
In the left “Components” panel:
- Drag **Processor** onto the canvas (3 times)

Choose these processors:
1. `ExecuteSQLRecord`
2. `UpdateAttribute`
3. `PutFile`

Arrange left → right.

#### Step 4 — Connect processors (success)
Draw connections:
- ExecuteSQLRecord → UpdateAttribute (relationship: **success**)
- UpdateAttribute → PutFile (relationship: **success**)

#### Step 5 — Configure PutFile (save into repo folder)
Right-click **PutFile** → Configure → Properties:

- Directory:
  ```
  <PROJECT_ROOT>\nifi
  ```
- Create Missing Directories = `true`
- Conflict Resolution Strategy = `replace` (recommended during testing)

Apply.

#### Step 6 — Configure UpdateAttribute (filename)
Right-click **UpdateAttribute** → Configure → Properties:

Add property:
- filename:
  ```
  books_${now():format("yyyyMMdd_HHmmss")}.json
  ```

Apply.

#### Step 7 — Configure ExecuteSQLRecord (SQL + JSON writer + DB connection)
Right-click **ExecuteSQLRecord** → Configure → Properties:

- SQL Query:
  ```sql
  SELECT * FROM books_import_py;
  ```

Create controller services:
- Database Connection Pooling Service → **Create new service** → `DBCPConnectionPool`
- Record Writer → **Create new service** → `JsonRecordSetWriter`

Apply.

#### Step 8 — Configure & Enable DBCPConnectionPool (MySQL)
Open the controller service and set:

- Database Connection URL:
  ```
  jdbc:mysql://localhost:3306/module15_cw1_de_py?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC
  ```
- Database Driver Class Name:
  ```
  com.mysql.cj.jdbc.Driver
  ```
- Database Driver Location(s):
  ```
  <NIFI_HOME>\nifi-2.7.2\lib\mysql-connector-j-9.6.0.jar
  ```
- Database User:
  ```
  root
  ```
- Password: (blank if XAMPP default)

Apply → **Enable**.

#### Step 9 — Configure & Enable JsonRecordSetWriter
Set:
- Pretty Print JSON = `true`
- (Optional) Output grouping = Single JSON Array (if available)

Apply → **Enable**.

#### Step 10 — Auto-terminate the failure relationship
ExecuteSQLRecord will complain unless you handle `failure`.

Right-click **ExecuteSQLRecord** → Configure → Settings:
- Auto-terminate relationships: ✅ `failure`

Apply.

---

### 8.5 Run it once (or stop it when you need to)

NiFi can run on a schedule, so you might see it exporting repeatedly.

**Easy method (recommended for beginners):**
- Start the processors
- Wait for one JSON file to appear
- Stop ExecuteSQLRecord when you’re done

#### Start order
Start (play button) in this order:
1. PutFile
2. UpdateAttribute
3. ExecuteSQLRecord

#### Output check
Open:
```
<PROJECT_ROOT>\nifi
```

You should see files like:
- `books_20260131_174210.json`

> If you want it to run less often:
> ExecuteSQLRecord → Configure → Scheduling → increase “Run Schedule” (e.g., `60 sec`).

---

### 8.6 What to record for your Task 3 video

Show these steps clearly:

1. **MySQL table exists** (phpMyAdmin: `SELECT COUNT(*) FROM books_import_py;`)
2. NiFi canvas with the full flow: ExecuteSQLRecord → UpdateAttribute → PutFile
3. ExecuteSQLRecord configuration:
   - SQL Query
   - DBCPConnectionPool enabled
   - JsonRecordSetWriter enabled
4. PutFile directory (inside your repo)
5. Start the flow and show the JSON file created
6. Open the JSON output file to prove it contains the data

---

### 8.7 Common errors and fixes

**“Not secure” on https://localhost:8443/nifi**  
- Normal for localhost (self-signed cert). Proceed anyway.

**Controller Service cannot enable**
- Check MySQL is running in XAMPP
- Check jar path is correct and NiFi was restarted after adding jar
- Driver class must be: `com.mysql.cj.jdbc.Driver`
- DB name in URL must match your database exactly

**ExecuteSQLRecord says failure relationship not connected**
- Auto-terminate relationship: `failure` (Settings tab)

**It exports every second**
- Stop ExecuteSQLRecord when finished, or increase “Run Schedule”

---

## 9. Task 4 — MongoDB (CSV → JSON → Compass import → Queries → Timing)

Task 4 requirements (from the coursework spec):
- Convert the Task 1 dataset to **JSON**
- Import JSON into **MongoDB**
- Run MongoDB queries (filter/retrieve/sort)
- Compare **query execution time** between **MongoDB** and **MySQL**
- Include screenshots + a written comparison in your report

This repo supports a **Compass-only** MongoDB workflow (no CLI tools needed).

---

### 9.1 Install MongoDB Community Server + Compass (Windows)

1. Download **MongoDB Community Server** (includes Compass option).
2. During installation:
   - Install MongoDB as a **Windows Service**
   - Install **MongoDB Compass**
3. Launch **MongoDB Compass**
4. Connect with the default local URI:
   ```
   mongodb://localhost:27017
   ```

If Compass connects successfully, MongoDB is running.

---

### 9.2 Convert CSV → JSON (Python)

**Input:** `data/processed/books.csv`  
**Outputs:**  
- `data/exports/books.json` (JSON array)  
- `data/exports/books.ndjson` (newline-delimited JSON)

> Why two outputs? Compass can import either JSON array or NDJSON.

#### Option A — Notebook (recommended)
Run:
- `notebooks/03_task4_mongodb_compass_and_benchmark.ipynb`

This notebook writes the JSON files to `data/exports/`.

#### Option B — Script (repeatable, robust paths)
Create/update this file:
- `src/task4_mongo/csv_to_json.py`

Run from the **project root**:
```powershell
python -m src.task4_mongo.csv_to_json
```

✅ This script is designed to work regardless of your working directory (it finds the project root automatically).

If you need to explicitly set paths:
```powershell
python -m src.task4_mongo.csv_to_json --csv "data/processed/books.csv" --out_dir "data/exports"
```

---

### 9.3 Import JSON into MongoDB Compass

We will import into:
- Database: `cw1_de`
- Collection: `books`

Steps:
1. In Compass, connect to `mongodb://localhost:27017`
2. Click **Create database**
   - Database Name: `cw1_de`
   - Collection Name: `books`
3. Open `cw1_de.books`
4. Click **Import Data**
5. Choose file:
   - `data/exports/books.json` (recommended)
6. Import

Verification:
- Go to **Documents** tab
- Confirm the document count ≈ CSV rows
- Click a document and confirm fields exist:
  - `title`, `authors`, `year`, `star_rating`, `price`, `source_url`

---

### 9.4 MongoDB queries (run inside Compass)

In Compass, open `cw1_de.books` → **Documents** tab.

Use the **Filter** and **Sort** boxes.

#### Query A — price ≥ 30, sort by price descending
Filter:
```json
{ "price": { "$gte": 30 } }
```
Sort:
```json
{ "price": -1 }
```

#### Query B — year ≥ 2020, sort by year descending
Filter:
```json
{ "year": { "$gte": 2020 } }
```
Sort:
```json
{ "year": -1 }
```

#### Query C — title contains “data” (case-insensitive)
Filter:
```json
{ "title": { "$regex": "data", "$options": "i" } }
```

---

### 9.5 Query execution time comparison (MongoDB vs MySQL)

For coursework evidence, a simple and fair comparison is:
- **same filter condition** (e.g., price ≥ 30)
- **same sort** (price descending)
- measure elapsed time in Python

#### Option A — Notebook (included)
Use the bottom section of:
- `notebooks/03_task4_mongodb_compass_and_benchmark.ipynb`

#### Option B — Script (recommended for repeatable timing)
Create/update:
- `src/task4_mongo/benchmark.py`

Install dependency (once):
```powershell
pip install pymongo
```

Run:
```powershell
python -m src.task4_mongo.benchmark --min_price 30
```

The benchmark prints:
- MySQL time + rows returned
- MongoDB time + rows returned

> Tip: For a more stable comparison, run the benchmark 3 times and take the average (optional).


## 10. End-to-end testing checklist

1. Create `.venv` and install requirements  
2. Start XAMPP (Apache + MySQL)  
3. Run **Task 1 notebook** → confirm `data/processed/books.csv` exists and has ≥ 15 rows  
4. Run **Task 2 notebook** → confirm DB/table exists and has rows  
5. Run SQL verification queries (3 columns + sorting)  
6. Build NiFi flow and export JSON into `./nifi/`  
7. Run Task 4: CSV → JSON export into `data/exports/`  
8. Import JSON into MongoDB (Compass) and run MongoDB queries  
9. Run timing comparison (MySQL vs MongoDB) and capture results  

---

## 11. Troubleshooting

### CSV import issues in phpMyAdmin
If UI import fails or columns misalign, use the code method:
```powershell
python -m src.task2_sql.run_task2_all --also-ui
```

### MySQL connection fails
- Ensure MySQL is running in XAMPP
- Check username/password
- Verify DB name and table name exist


