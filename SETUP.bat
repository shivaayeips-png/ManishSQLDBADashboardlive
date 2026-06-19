@echo off
REM SQL Server Monitoring - Python Setup Script
REM This script installs all required Python dependencies

echo ========================================
echo SQL Server Monitoring - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    echo Please install pip
    pause
    exit /b 1
)

echo Installing Python dependencies...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit monitoring_config.json with your server details
echo 2. Run START_MONITORING.bat to begin monitoring
echo 3. Or run individual scripts:
echo    - python collect_sql_metrics.py (collect metrics once)
echo    - python alert_system.py (check alerts)
echo    - python dashboard_api.py (start API server)
echo    - python scheduler.py (automated monitoring)
echo.
pause

@REM Made with Bob
