@echo off
cd /d "%~dp0backend"
echo Installing project dependencies + pytest...
call "%~dp0.venv\Scripts\python.exe" -m pip install -r requirements.txt pytest -q
echo.
echo Running tests...
"%~dp0.venv\Scripts\python.exe" -m pytest tests/ -v
echo.
echo Done.
pause
