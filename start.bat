@echo off
title ScoutVision Launcher
cd /d "%~dp0"
set "BACKEND_PORT=8010"
set "FRONTEND_PORT=5174"

echo ===================================
echo       ScoutVision - Starting Up
echo ===================================
echo.

where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker CLI was not found. Install Docker Desktop and try again.
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    if exist "%ProgramFiles%\Docker\Docker\Docker Desktop.exe" (
        echo Starting Docker Desktop...
        start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
    ) else (
        echo [ERROR] Docker Desktop is not running and was not found in its default location.
        echo Open Docker Desktop manually, wait until it is ready, then run start.bat again.
        pause
        exit /b 1
    )
)

echo Waiting for Docker Desktop...
set /a docker_attempts=0
:wait_docker
    docker info >nul 2>&1
    if not errorlevel 1 goto docker_ready
    set /a docker_attempts+=1
    if %docker_attempts% GEQ 90 goto docker_timeout
    timeout /t 2 /nobreak >nul
    goto wait_docker

:docker_timeout
echo [ERROR] Docker did not become ready after 3 minutes.
echo Check Docker Desktop, then run start.bat again.
pause
exit /b 1

:docker_ready
echo Docker is ready. Building and starting ScoutVision...
start "ScoutVision Docker" /D "%~dp0" cmd /k docker compose up --build

echo Waiting for ScoutVision to respond at http://localhost:%FRONTEND_PORT% ...
set /a app_attempts=0
:wait_app
    curl.exe --fail --silent "http://localhost:%FRONTEND_PORT%/health" >nul 2>&1
    if not errorlevel 1 goto app_ready
    set /a app_attempts+=1
    if %app_attempts% GEQ 180 goto app_timeout
    timeout /t 2 /nobreak >nul
    goto wait_app

:app_timeout
echo [ERROR] ScoutVision did not respond after 6 minutes.
echo Check the ScoutVision Docker window for build or startup errors.
pause
exit /b 1

:app_ready
echo ScoutVision is ready. Opening your browser...
start "" "http://localhost:%FRONTEND_PORT%"
echo.
echo To stop ScoutVision, press Ctrl+C in the ScoutVision Docker window.
pause
