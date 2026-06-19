@echo off
REM SQL Server Monitoring - Start API Server
REM This script starts the Flask REST API server

echo ========================================
echo SQL Server Monitoring - API Server
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

echo Starting Flask API server...
echo.
echo API will be available at: http://localhost:5000
echo.
echo Available endpoints:
echo - GET /api/health
echo - GET /api/monitoring/dashboard
echo - GET /api/monitoring/servers
echo - GET /api/monitoring/databases
echo - GET /api/monitoring/performance/^<server^>
echo - GET /api/monitoring/config
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

python dashboard_api.py

if errorlevel 1 (
    echo.
    echo ERROR: API server failed to start
    echo Check the logs for details
    pause
    exit /b 1
)

@REM Made with Bob
