@echo off
REM ========================================
REM SQL Server Monitoring Dashboard
REM Complete Setup and Launch Script
REM ========================================

echo.
echo ========================================
echo SQL Server Monitoring Dashboard
echo Complete Setup and Launch
echo ========================================
echo.

cd /d "%~dp0"

REM Step 1: Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
python --version
echo Python found!
echo.

REM Step 2: Install Python packages
echo [2/5] Installing Python packages...
echo This may take a few minutes...
echo.
python -m pip install --upgrade pip
python -m pip install pyodbc flask flask-cors schedule

if errorlevel 1 (
    echo.
    echo WARNING: Some packages may have failed to install
    echo Continuing anyway...
    echo.
)
echo Packages installed!
echo.

REM Step 3: Create monitoring database
echo [3/5] Creating monitoring database...
echo.
echo Connecting to SQL Server: 00670T744\MANISHPREET
echo.

sqlcmd -S "00670T744\MANISHPREET" -U manish -P "manish@79" -Q "IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'SQLServerMonitoring') CREATE DATABASE SQLServerMonitoring" >nul 2>&1

if errorlevel 1 (
    echo WARNING: Could not create database automatically
    echo You may need to create it manually
    echo.
) else (
    echo Database check complete!
    echo.
)

REM Step 4: Start API server in background
echo [4/5] Starting Python API server...
echo.
start "SQL Monitoring API" /MIN python dashboard_api.py

echo Waiting for API to start...
timeout /t 5 /nobreak >nul
echo API server started!
echo.

REM Step 5: Open dashboard
echo [5/5] Opening dashboard in browser...
echo.

start "" "dashboard.html"

echo.
echo ========================================
echo Dashboard Setup Complete!
echo ========================================
echo.
echo The dashboard should open in your browser automatically.
echo.
echo Dashboard file: dashboard.html
echo API Server: http://localhost:5000
echo.
echo IMPORTANT:
echo - A minimized window is running the API server
echo - Do NOT close that window
echo - To stop monitoring, close the minimized window
echo.
echo If dashboard doesn't show data:
echo 1. Wait 10 seconds and refresh the page
echo 2. Check if API is running: http://localhost:5000/api/health
echo 3. Check the minimized API server window for errors
echo.
echo ========================================
echo.
pause

@REM Made with Bob
