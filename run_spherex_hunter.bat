@echo off
setlocal
cd /d "%~dp0"
title SPHEREx Hunter - NASA Space Apps 2026 (Team RIP)
color 0B

echo ==============================================================================
echo       [*] SPHEREx HUNTER: TIME-DOMAIN ASTRONOMICAL SKY VIEWER [*]
echo                 NASA Space Apps Challenge 2026 - Team RIP
echo ==============================================================================
echo.

REM 1. Verify Python availability (.venv preferred)
if exist .venv\Scripts\python.exe (
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    set PYTHON_CMD=python
)
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python was not found in your system PATH or .venv!
    echo Please install Python 3.10+ from https://www.python.org/ and check "Add to PATH".
    echo.
    pause
    exit /b 1
)

REM 2. Check and clean up orphaned port 8000 if already running
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [INFO] Detected previous server instance on port 8000 PID %%a. Cleaning up...
    taskkill /F /PID %%a >nul 2>&1
)

echo [1/3] Initializing SPHEREx Astro-Backend (FastAPI + Astropy)...
echo [2/3] Connecting to NASA IRSA / Caltech FinderChart / SkyView Archive...
echo [3/3] Launching interactive web viewer in your default browser...
echo.
echo ------------------------------------------------------------------------------
echo   Web Application URL  : http://localhost:8000/app/index.html
echo   Interactive API Docs : http://localhost:8000/docs
echo   Backend Health Check : http://localhost:8000/api/health
echo ------------------------------------------------------------------------------
echo.
echo [NOTE] Keep this window OPEN while using the app. Press Ctrl+C to stop.
echo.

REM Launch browser in background after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000/app/index.html"

REM Run FastAPI uvicorn server
%PYTHON_CMD% -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

echo.
echo Server stopped.
pause
