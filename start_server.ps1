# PowerShell script to start server with UTF-8 encoding
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Starting game server with UTF-8 encoding..." -ForegroundColor Green
& "C:\Users\KO\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn web_server:app --host 0.0.0.0 --port 8000 --reload
