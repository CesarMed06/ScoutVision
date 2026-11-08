@echo off
title ScoutVision Tests
cd /d "%~dp0backend"

set "PYTHON=python"
py -3.12 -V >nul 2>&1
if not errorlevel 1 set "PYTHON=py -3.12"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info.major == 3 and sys.version_info.minor == 12 else 1)" >nul 2>&1
    if errorlevel 1 (
        echo Existing virtual environment uses another Python version. Recreating it...
        rmdir /s /q ".venv"
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment with %PYTHON% ...
    %PYTHON% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Could not create the virtual environment.
        echo Install Python 3.12 from https://www.python.org/downloads/ and try again.
        pause
        exit /b 1
    )
)

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Could not install the backend dependencies.
    echo The pinned versions target Python 3.12; newer interpreters may fail to build them.
    pause
    exit /b 1
)

echo.
echo Running tests...
".venv\Scripts\python.exe" -m pytest tests/ -v
echo.
echo Done.
pause
