@echo off
REM SQL Server Monitoring - Start Automated Monitoring
REM This script starts the automated monitoring scheduler

echo ========================================
echo SQL Server Monitoring - Starting
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run SETUP.bat first
    pause
    exit /b 1
)

REM Check if config file exists
if not exist "monitoring_config.json" (
    echo ERROR: monitoring_config.json not found
    echo Please create the configuration file first
    pause
    exit /b 1
)

echo Starting automated monitoring...
echo.
echo The scheduler will:
echo - Collect metrics every 30 seconds
echo - Check alerts every 5 minutes
echo - Log all activities to scheduler.log
echo.
echo Press Ctrl+C to stop monitoring
echo.
echo ========================================
echo.

python scheduler.py

if errorlevel 1 (
    echo.
    echo ERROR: Monitoring failed to start
    echo Check the logs for details
    pause
    exit /b 1
)

@REM Made with Bob
