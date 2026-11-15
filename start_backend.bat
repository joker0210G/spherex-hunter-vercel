@echo off
title SPHEREx Hunter - Astronomical API Backend
echo ========================================================
echo   STARTING SPHEREX HUNTER BACKEND (FASTAPI / ASTROPY)
echo ========================================================
echo.
echo Connecting to NASA IRSA / SkyView Archives...
echo API Docs will be available at: http://localhost:8000/docs
echo Health Check: http://localhost:8000/api/health
echo.
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
