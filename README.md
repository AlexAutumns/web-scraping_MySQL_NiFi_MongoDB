# How to Start?

## Creating Python Environment

### Check if Python is Installed and What Version
```powershell
python --version
```
If that fails, try:
```powershell
py --version
```

If both fail, install **Python** from [python.org](https://www.python.org) and tick `"Add Python to PATH"` during install.



### Create Virtual Environment (venv)
**Inside project folder**

```powershell
py -m venv .venv
```
This creates a hidden-ish folder .venv/ that contains an isolated Python + pip.


### Activate the venv
**Powershell**
```powershell
./.venv/Scripts/Activate.ps1
```
or
```powershell
.\.venv\Scripts\Activate.ps1
```
If in VSCode, check if you are using the right Python Interpreter

### Confirm if you are suing the venv Python
```powershell
where python
python -c "import sys; print(sys.executable)"
```

### Upgrade pip (recommended)
```powershell
python -m pip install --upgrade pip
```

### Install Packages
```powershell
pip install -r requirements.txt
```

You should see paths pointing into: `.venv\Scripts\python.exe`

### Deactivate when done
```powershell
deactivate
```



## Task 1 - Web Scraping
**Inside project folder**

### Run the Manning scraping script
```powershell
python -m src.task1_scrape.manning_run
```
It gets it sources from `/src/task1_scrape/sources.py`, using sources from [Manning](https://www.manning.com).

Results saved in `data/processed/` and `data/raw/`



## Task 2 - SQL Database

### Start Services
Open **XAMPP Control Panel**:
- Start Apache
- Start MySQL


### Create Database (If you haven't yet)

Open [`http://localhost/phpmyadmin`](http://localhost/phpmyadmin)

1. Click **New**
2. Database Name: `module15_cw1_de`
3. Collation: leave default (`utf8mb4_general_ci` is fine)
4. Click **Create**

## Task 2A - UI Import

### Create `books_import_ui` table

Go to database **module15_cw1_de** -> click **SQL tab** -> paste and run:
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

### Import CSV using phpMyAdmin UI
1. Click table: `books_import_ui`
2. Click **Import**
3. Choose file: `data/processed/books.csv`
4. Format: **CSV**
5. Important settings:
   - **The first line of the file contains the table column names** ✅ (tick this if available)
   - Column separator: `,`
   - Enclosure: `"`
   - Escape: `\`
6. Click **Import**

### Verification Queries

**Basic Check**
```sql
SELECT COUNT(*) AS row_count
FROM books_import_ui;
```

**3 Columns and 'ORDER BY'**
```sql
SELECT title, authors, price
FROM books_import_ui
ORDER BY price DESC;
```

**Year Sorting**
```sql
SELECT title, year, price
FROM books_import_ui
ORDER BY year DESC, price DESC;
```

## Task 2B - Code Import

### Create `books_import_py` table
```sql
DROP TABLE IF EXISTS books_import_py;

CREATE TABLE books_import_py (
  title VARCHAR(255) NOT NULL,
  authors TEXT NOT NULL,
  year INT NOT NULL,
  star_rating FLOAT NULL,
  price DECIMAL(10,2) NOT NULL,
  source_url TEXT NOT NULL
);
```

### Add an `.env` file for credentials (not included in Git commits)
Create `.env` in project root:
```env
DB_HOST=
DB_PORT=3306
DB_NAME=module15_cw1_de
DB_USER=
DB_PASSWORD=
```
Edit your variables based on your MySQL

### Run Import Script
```powershell
python -m src.task2_sql.import_csv
```

After running you should see this in the terminal:
```powershell
[OK] Inserted rows: 15
```


### Verification Queries

**Basic Check**
```sql
SELECT COUNT(*) AS row_count
FROM books_import_py;
```

**3 Columns and 'ORDER BY'**
```sql
SELECT title, authors, price
FROM books_import_py
ORDER BY price DESC;
```

**Year Sorting**
```sql
SELECT title, year, price
FROM books_import_py
ORDER BY year DESC, price DESC;
```