@echo off
echo ============================================
echo Customer SQL Server Monitoring Dashboard
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/3] Setting up database tables...
echo.
sqlcmd -S 00670T744\MANISHPREET -U manish -P manish@79 -d SQLServerMonitoring -i sql\Create-CustomerTables.sql
if errorlevel 1 (
    echo WARNING: Database setup may have failed. Continuing anyway...
    echo.
)

echo.
echo [2/3] Starting Flask API Server...
echo API will be available at http://localhost:5000
echo.
start "Customer Monitoring API" cmd /k python dashboard_api.py

REM Wait for API to start
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Opening Customer Dashboard...
echo.
start customer_dashboard.html

echo.
echo ============================================
echo Dashboard is now running!
echo ============================================
echo.
echo Dashboard URL: file:///%CD%/customer_dashboard.html
echo API URL: http://localhost:5000
echo.
echo Available Endpoints:
echo   - GET /api/monitoring/customers
echo   - GET /api/monitoring/customers/{id}
echo   - GET /api/monitoring/customers/{id}/status
echo.
echo To monitor customers via command line:
echo   python customer_monitoring.py
echo.
echo Press any key to stop the API server...
pause >nul

REM Stop the API server
taskkill /FI "WINDOWTITLE eq Customer Monitoring API*" /T /F >nul 2>&1

echo.
echo Dashboard stopped.
pause

@REM Made with Bob
