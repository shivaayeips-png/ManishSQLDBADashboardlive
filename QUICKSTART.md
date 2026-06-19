# SQL Server Monitoring - Quick Start Guide

Get your SQL Server monitoring dashboard up and running in 5 minutes!

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Dependencies (2 minutes)

Double-click `SETUP.bat` or run:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Servers (1 minute)

Edit `monitoring_config.json`:
```json
{
  "monitoring_server": {
    "server": "localhost",
    "database": "SQLServerMonitoring",
    "use_windows_auth": true
  },
  "target_servers": [
    "localhost"
  ]
}
```

### Step 3: Create Database (1 minute)

Run from PowerShell:
```powershell
cd ..\sql-genius-main
sqlcmd -S localhost -i sql\Create-MonitoringDatabase.sql
```

### Step 4: Start Monitoring (1 minute)

Double-click `START_MONITORING.bat` or run:
```bash
python scheduler.py
```

## ✅ Verify Installation

### Test 1: Collect Metrics Once
```bash
python collect_sql_metrics.py
```

Expected output:
```
=== SQL Server Monitoring Data Collection ===
Collecting metrics for: localhost
✓ Server localhost is ONLINE (Response: 45ms)
  CPU: 25.5% | Memory: 65.2% | Connections: 10
  Found 7 user databases
✓ Saved metrics for server: localhost
```

### Test 2: Check Alerts
```bash
python alert_system.py
```

Expected output:
```
=== SQL Server Alert Check ===
✓ No alerts detected - all systems normal
```

### Test 3: Start API
```bash
python dashboard_api.py
```

Then open browser: http://localhost:5000/api/health

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-06-14T15:30:00"
}
```

## 📊 View Dashboard

### Option 1: Use Existing React Dashboard

The Python API is compatible with the existing dashboard at:
```
http://localhost:5173/monitoring
```

### Option 2: Use API Directly

Access endpoints:
- Dashboard: http://localhost:5000/api/monitoring/dashboard
- Servers: http://localhost:5000/api/monitoring/servers
- Databases: http://localhost:5000/api/monitoring/databases

## 🎯 Common Tasks

### Collect Metrics Manually
```bash
python collect_sql_metrics.py
```

### Check for Alerts
```bash
python alert_system.py
```

### Start API Server
```bash
python dashboard_api.py
# or double-click START_API.bat
```

### Start Automated Monitoring
```bash
python scheduler.py
# or double-click START_MONITORING.bat
```

## 🔧 Configuration Examples

### Monitor Multiple Servers
```json
{
  "target_servers": [
    "SERVER1",
    "SERVER2",
    "SERVER3\\INSTANCE1"
  ]
}
```

### Adjust Collection Interval
```json
{
  "collection_interval_seconds": 60
}
```

### Configure Alert Thresholds
```json
{
  "alert_thresholds": {
    "cpu_percent": 80,
    "memory_percent": 85,
    "blocked_sessions": 5,
    "response_time_ms": 1000
  }
}
```

### Enable Email Alerts
```json
{
  "email_alerts": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "alerts@yourdomain.com",
    "to_emails": ["admin@yourdomain.com"],
    "username": "your-email@gmail.com",
    "password": "your-app-password"
  }
}
```

## 🐛 Troubleshooting

### Python Not Found
Install Python 3.8+ from: https://www.python.org/downloads/

### ODBC Driver Not Found
Install from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Connection Failed
1. Check SQL Server is running
2. Verify server name in config
3. Test connection:
```python
import pyodbc
conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;Trusted_Connection=yes;")
print("Connected!")
```

### Permission Denied
Grant permissions:
```sql
USE SQLServerMonitoring;
GRANT SELECT, INSERT ON SCHEMA::dbo TO [YourUser];
GRANT EXECUTE ON SCHEMA::dbo TO [YourUser];
```

## 📁 File Overview

| File | Purpose |
|------|---------|
| `collect_sql_metrics.py` | Collect server metrics |
| `alert_system.py` | Check and send alerts |
| `dashboard_api.py` | REST API server |
| `scheduler.py` | Automated monitoring |
| `monitoring_config.json` | Configuration |
| `requirements.txt` | Python dependencies |
| `SETUP.bat` | Install dependencies |
| `START_MONITORING.bat` | Start monitoring |
| `START_API.bat` | Start API server |

## 🎓 Next Steps

1. **Customize Alerts**: Edit thresholds in config
2. **Add More Servers**: Update target_servers list
3. **Enable Email**: Configure SMTP settings
4. **Schedule as Service**: Use Windows Task Scheduler
5. **View Logs**: Check `scheduler.log` and `sql_monitoring.log`

## 📞 Need Help?

1. Check logs for errors
2. Review README.md for detailed docs
3. Test individual components
4. Verify database connectivity

## 🎉 Success!

You now have:
- ✅ Automated metrics collection
- ✅ Real-time monitoring
- ✅ Alert system
- ✅ REST API
- ✅ Dashboard integration

**Happy Monitoring!** 🚀

---

Made with Bob | Version 1.0.0