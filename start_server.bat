@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo Starting game server with UTF-8 encoding...
C:\Users\KO\AppData\Local\Programs\Python\Python311\python.exe -m uvicorn web_server:app --host 0.0.0.0 --port 8000 --reload
