Write-Host "Creating virtual environment..."
python -m venv .venv

Write-Host "Upgrading pip..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip

Write-Host "Installing dependencies..."
.\.venv\Scripts\pip.exe install -r requirements.txt

Write-Host "Running config setup..."
.\.venv\Scripts\python.exe scripts/config.py

Write-Host "Setup complete ✅"
