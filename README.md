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