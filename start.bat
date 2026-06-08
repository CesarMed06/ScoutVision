@echo off
title ScoutVision Launcher
echo ===================================
echo       ScoutVision - Starting Up
echo ===================================
echo.

:: Delete old index so it rebuilds with latest fixes (Messi, etc.)
if exist "%~dp0backend\data\players_index.json" (
    del "%~dp0backend\data\players_index.json"
    echo [1/3] Old index deleted - will rebuild with Messi and fixes...
) else (
    echo [1/3] No old index found - will create fresh...
)
echo.

:: Start Backend
start "ScoutVision Backend" cmd /c "cd /d %~dp0backend && %~dp0.venv\Scripts\python.exe -m uvicorn app.main:app --reload"
echo [2/3] Backend starting...  (http://localhost:8000)
echo.

:: Small pause so backend starts first
ping -n 3 127.0.0.1 >nul

:: Start Frontend
start "ScoutVision Frontend" cmd /c "cd /d %~dp0frontend && npm run dev"
echo [3/3] Frontend starting... (http://localhost:5173)
echo.
echo ===================================
echo  Open http://localhost:5173 in browser
echo ===================================
echo.
echo Close this window to stop both.
pause
