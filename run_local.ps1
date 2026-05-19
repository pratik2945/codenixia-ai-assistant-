# Run Codenixia AI Assistant locally (Windows)
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path "venv")) {
    python -m venv venv
    .\venv\Scripts\pip install -r requirements.txt
}

if (-not (Test-Path ".env")) {
    # Copy as UTF-8 (avoid UTF-16 from Notepad breaking python-dotenv)
    python -c "from pathlib import Path; Path('.env').write_text(Path('.env.example').read_text(encoding='utf-8'), encoding='utf-8')"
    Write-Host "Created .env from .env.example - add your API keys before using LLM features."
}

Write-Host "Starting FastAPI on http://localhost:8000 ..."
Start-Process -FilePath "$root\venv\Scripts\uvicorn.exe" -ArgumentList "app.main:app","--reload","--port","8000" -WorkingDirectory $root

Start-Sleep -Seconds 3

Write-Host "Starting Streamlit on http://localhost:8501 ..."
& "$root\venv\Scripts\streamlit.exe" run frontend/streamlit_app.py
