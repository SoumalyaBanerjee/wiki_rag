Write-Host "Starting Docker Desktop..."
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

Write-Host "Waiting for Docker..."
while (-not (docker info 2>$null)) {
    Start-Sleep -Seconds 3
}

Write-Host "Starting Qdrant..."
docker-compose up -d

Write-Host "Launching Streamlit..."
.\.venv\Scripts\streamlit.exe run scripts/6.streamlit_app.py
