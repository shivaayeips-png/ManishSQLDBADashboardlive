@echo off
REM GXO SQL Server Monitoring - Production Dashboard Launcher
REM This script starts the API server and opens the production dashboard

echo ========================================
echo GXO SQL Server Monitoring Dashboard
echo Production Environment
echo ========================================
echo.

REM Check if Python is installed
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Checking configuration files...
if not exist "monitoring_config.json" (
    echo ERROR: monitoring_config.json not found
    echo Please create the configuration file first
    pause
    exit /b 1
)

if not exist "customer_config.json" (
    echo ERROR: customer_config.json not found
    echo Please create the customer configuration file first
    pause
    exit /b 1
)

echo [2/3] Starting API server on port 7070...
echo.
echo API Endpoints:
echo   - Dashboard: http://localhost:7070/monitoring
echo   - Customers: http://localhost:7070/api/monitoring/customers
echo   - Server Details: http://localhost:7070/api/monitoring/server-details
echo.

REM Start the API server in a new window
start "GXO Monitoring API Server" py dashboard_api.py

REM Wait for server to start
echo [3/3] Waiting for API server to start...
timeout /t 5 /nobreak >nul

REM Open the production dashboard in default browser
echo Opening production dashboard...
start http://localhost:7070/monitoring

echo.
echo ========================================
echo Dashboard is now running!
echo ========================================
echo.
echo Dashboard URL: http://localhost:7070/monitoring
echo.
echo IMPORTANT: Keep the API server window open!
echo Close the API server window to stop the dashboard.
echo.
echo Press any key to exit this window...
pause >nul

@REM Made with Bob
