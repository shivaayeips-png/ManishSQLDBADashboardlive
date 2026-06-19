# Troubleshooting Guide - SQL Server Monitoring

## 🔴 Issue: Cannot Connect to localhost:5000

### Quick Fix Steps:

#### Step 1: Check if Python is Installed
```bash
python --version
```
Expected: Python 3.8 or higher

#### Step 2: Install Dependencies
```bash
cd C:\Users\00670T744\Videos\Python_SQLDBA
pip install -r requirements.txt
```

#### Step 3: Start the API Server
```bash
python dashboard_api.py
```

Or double-click: `START_API.bat`

#### Step 4: Verify Server is Running
You should see:
```
Starting SQL Server Monitoring Dashboard API...
API will be available at http://localhost:5000
 * Running on http://0.0.0.0:5000
```

#### Step 5: Test the Connection
Open browser: http://localhost:5000/api/health

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-06-14T15:30:00"
}
```

## 🔍 Common Issues & Solutions

### Issue 1: Python Not Found
**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Install Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart terminal/command prompt

### Issue 2: pip Not Found
**Error**: `'pip' is not recognized`

**Solution**:
```bash
python -m ensurepip --upgrade
```

### Issue 3: Module Not Found (pyodbc, flask, etc.)
**Error**: `ModuleNotFoundError: No module named 'pyodbc'`

**Solution**:
```bash
pip install pyodbc flask flask-cors schedule
```

Or run:
```bash
pip install -r requirements.txt
```

### Issue 4: ODBC Driver Not Found
**Error**: `[Microsoft][ODBC Driver Manager] Data source name not found`

**Solution**:
1. Download ODBC Driver 17 for SQL Server
2. Install from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
3. Restart your application

### Issue 5: Port 5000 Already in Use
**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

Or change port in `dashboard_api.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Issue 6: Cannot Connect to SQL Server
**Error**: `Login failed for user` or `Cannot open database`

**Solution**:
1. Verify SQL Server is running
2. Check server name in `monitoring_config.json`
3. Verify Windows Authentication or credentials
4. Test connection:
```python
import pyodbc
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "Trusted_Connection=yes;"
)
print("Connected!")
```

### Issue 7: Monitoring Database Not Found
**Error**: `Cannot open database "SQLServerMonitoring"`

**Solution**:
Create the database first:
```bash
cd ..\sql-genius-main
sqlcmd -S localhost -i sql\Create-MonitoringDatabase.sql
```

### Issue 8: Permission Denied
**Error**: `The SELECT permission was denied`

**Solution**:
Grant permissions:
```sql
USE SQLServerMonitoring;
GRANT SELECT, INSERT ON SCHEMA::dbo TO [YourUser];
GRANT EXECUTE ON SCHEMA::dbo TO [YourUser];
```

## 🧪 Testing Individual Components

### Test 1: Python Installation
```bash
python --version
pip --version
```

### Test 2: Import Modules
```bash
python -c "import pyodbc; print('pyodbc OK')"
python -c "import flask; print('flask OK')"
python -c "import schedule; print('schedule OK')"
```

### Test 3: SQL Server Connection
```bash
python -c "import pyodbc; conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;Trusted_Connection=yes;'); print('SQL Server Connected!')"
```

### Test 4: Collect Metrics Once
```bash
python collect_sql_metrics.py
```

### Test 5: Check Alerts
```bash
python alert_system.py
```

### Test 6: Start API
```bash
python dashboard_api.py
```

## 📋 Pre-Flight Checklist

Before starting the monitoring system:

- [ ] Python 3.8+ installed
- [ ] pip working
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] ODBC Driver 17 for SQL Server installed
- [ ] SQL Server running
- [ ] Monitoring database created
- [ ] `monitoring_config.json` configured
- [ ] Firewall allows connections (if needed)
- [ ] Port 5000 available

## 🔧 Manual API Start (Step-by-Step)

1. **Open Command Prompt or PowerShell**
```bash
cd C:\Users\00670T744\Videos\Python_SQLDBA
```

2. **Verify Python**
```bash
python --version
```

3. **Install Dependencies (if not done)**
```bash
pip install flask flask-cors pyodbc
```

4. **Check Configuration**
```bash
type monitoring_config.json
```

5. **Start API Server**
```bash
python dashboard_api.py
```

6. **Keep Terminal Open**
Don't close the terminal - the API runs in foreground

7. **Test in Browser**
Open: http://localhost:5000/api/health

## 🌐 Alternative: Use Existing Node.js API

If Python API has issues, you can use the existing Node.js/TypeScript API:

```bash
cd C:\Users\00670T744\Videos\sql-genius-main
npm install
npm run dev
```

Dashboard will be at: http://localhost:5173/monitoring

## 📞 Still Having Issues?

### Check Logs
1. Look for error messages in terminal
2. Check `sql_monitoring.log`
3. Check `scheduler.log`

### Verify Configuration
```bash
python -c "import json; print(json.load(open('monitoring_config.json')))"
```

### Test Each Component
1. Test Python: `python --version`
2. Test imports: `python -c "import pyodbc, flask"`
3. Test SQL: `sqlcmd -S localhost -Q "SELECT @@VERSION"`
4. Test API: `python dashboard_api.py`

### Get Detailed Error
Run with verbose output:
```bash
python -v dashboard_api.py
```

## 🎯 Quick Recovery Commands

```bash
# Full reset and restart
cd C:\Users\00670T744\Videos\Python_SQLDBA
pip uninstall -y pyodbc flask flask-cors schedule
pip install -r requirements.txt
python dashboard_api.py
```

## 📝 Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Missing Python package | `pip install <package>` |
| `Connection refused` | API not running | Start with `python dashboard_api.py` |
| `Port already in use` | Another app using port 5000 | Kill process or change port |
| `ODBC Driver not found` | Driver not installed | Install ODBC Driver 17 |
| `Login failed` | SQL auth issue | Check credentials/Windows auth |
| `Database not found` | DB not created | Run Create-MonitoringDatabase.sql |

---

**Need More Help?**
1. Check the terminal output for specific errors
2. Review README.md for detailed setup
3. Verify all prerequisites are met
4. Test components individually

**Made with Bob** | Last Updated: 2026-06-14