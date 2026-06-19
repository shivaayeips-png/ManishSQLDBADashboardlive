# SQL Server Monitoring Dashboard - Python Implementation

Complete Python-based monitoring solution for SQL Server with PowerShell integration.

## 📋 Features

- **Real-time Metrics Collection**: Automated collection of server availability, performance, and database metrics
- **Alert System**: Configurable thresholds with email notifications
- **REST API**: Flask-based API for dashboard integration
- **Automated Scheduling**: Background service for continuous monitoring
- **Multi-Server Support**: Monitor multiple SQL Server instances
- **PowerShell Integration**: Works alongside existing PowerShell scripts

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **ODBC Driver 17 for SQL Server** installed
3. **SQL Server** with monitoring database created
4. **PowerShell 5.1+** (for PowerShell scripts)

### Installation

1. **Install Python Dependencies**
```bash
cd C:\Users\00670T744\Videos\Python_SQLDBA
pip install -r requirements.txt
```

2. **Configure Monitoring**

Edit `monitoring_config.json`:
```json
{
  "monitoring_server": {
    "server": "your-server-name",
    "database": "SQLServerMonitoring",
    "use_windows_auth": true
  },
  "target_servers": [
    "server1",
    "server2"
  ],
  "collection_interval_seconds": 30,
  "alert_thresholds": {
    "cpu_percent": 80,
    "memory_percent": 85,
    "blocked_sessions": 5,
    "response_time_ms": 1000
  }
}
```

3. **Create Monitoring Database**

Run the SQL script from the main project:
```bash
sqlcmd -S localhost -i ..\sql-genius-main\sql\Create-MonitoringDatabase.sql
```

## 📊 Usage

### 1. Manual Metrics Collection

Collect metrics once:
```bash
python collect_sql_metrics.py
```

### 2. Run Alert System

Check for alerts:
```bash
python alert_system.py
```

### 3. Start API Server

Start the Flask API:
```bash
python dashboard_api.py
```

API will be available at `http://localhost:5000`

### 4. Automated Monitoring (Recommended)

Start the scheduler for continuous monitoring:
```bash
python scheduler.py
```

This will:
- Collect metrics every 30 seconds (configurable)
- Check alerts every 5 minutes
- Log all activities to `scheduler.log`

## 🔌 API Endpoints

### Dashboard Summary
```
GET /api/monitoring/dashboard
```

Returns:
```json
{
  "serverSummary": {
    "TotalServers": 2,
    "AvailableServers": 2,
    "UnavailableServers": 0,
    "AvgResponseTimeMs": 45.5
  },
  "databaseSummary": {
    "TotalDatabases": 7,
    "OnlineDatabases": 7,
    "OfflineDatabases": 0,
    "TotalSizeMB": 1024.5
  },
  "performanceSummary": {
    "AvgCPUUsage": 35.2,
    "AvgMemoryUsage": 65.8,
    "TotalActiveConnections": 15,
    "TotalBlockedSessions": 0
  },
  "recentAlerts": []
}
```

### Server Status
```
GET /api/monitoring/servers
GET /api/monitoring/servers?server=server1
```

### Database Status
```
GET /api/monitoring/databases
GET /api/monitoring/databases?server=server1
```

### Performance History
```
GET /api/monitoring/performance/server1?hours=24
```

### Configuration
```
GET /api/monitoring/config
```

## 🔔 Alert Configuration

### Email Alerts

Enable email alerts in `monitoring_config.json`:
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

### Alert Types

- **SERVER_DOWN**: Server is unavailable
- **HIGH_CPU**: CPU usage exceeds threshold
- **HIGH_MEMORY**: Memory usage exceeds threshold
- **BLOCKED_SESSIONS**: Blocked sessions detected
- **DATABASE_OFFLINE**: Database is not online

## 🔧 PowerShell Integration

### Collect Metrics with PowerShell

```powershell
# From main project directory
cd ..\sql-genius-main

# Single collection
.\powershell\Collect-SQLServerMetrics.ps1 -ServerInstance "localhost" -TargetServers @("server1", "server2")

# Multi-server collection
.\powershell\Collect-MultiServer-Metrics.ps1
```

### Setup Windows Service

```powershell
.\powershell\Setup-WindowsService.ps1
```

## 📁 File Structure

```
Python_SQLDBA/
├── collect_sql_metrics.py    # Metrics collection script
├── alert_system.py            # Alert monitoring system
├── dashboard_api.py           # Flask REST API
├── scheduler.py               # Automated scheduler
├── monitoring_config.json     # Configuration file
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── SETUP.bat                  # Quick setup script
└── START_MONITORING.bat       # Start monitoring script
```

## 🐛 Troubleshooting

### ODBC Driver Not Found

Install ODBC Driver 17:
```bash
# Download from Microsoft
https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### Connection Issues

1. Check SQL Server is running
2. Verify firewall allows connections
3. Test connection string:
```python
import pyodbc
conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;Trusted_Connection=yes;")
```

### Permission Issues

Grant necessary permissions:
```sql
USE SQLServerMonitoring;
GRANT SELECT, INSERT ON SCHEMA::dbo TO [YourUser];
GRANT EXECUTE ON SCHEMA::dbo TO [YourUser];
```

## 🔐 Security Best Practices

1. **Use Windows Authentication** when possible
2. **Encrypt connection strings** in production
3. **Limit database permissions** to monitoring user
4. **Secure API endpoints** with authentication
5. **Use environment variables** for sensitive data

## 📈 Performance Optimization

1. **Adjust collection interval** based on needs
2. **Archive old data** regularly
3. **Index monitoring tables** for better query performance
4. **Use connection pooling** for high-frequency queries

## 🔄 Maintenance

### Clean Old Data

```sql
-- Delete data older than 30 days
DELETE FROM ServerAvailability WHERE CheckTime < DATEADD(DAY, -30, GETDATE());
DELETE FROM PerformanceMetrics WHERE CollectionTime < DATEADD(DAY, -30, GETDATE());
DELETE FROM DatabaseAvailability WHERE CheckTime < DATEADD(DAY, -30, GETDATE());
```

### Backup Monitoring Database

```powershell
Backup-SqlDatabase -ServerInstance "localhost" -Database "SQLServerMonitoring" -BackupFile "C:\Backups\SQLServerMonitoring.bak"
```

## 📝 Logging

All scripts log to their respective log files:
- `sql_monitoring.log` - Metrics collection
- `scheduler.log` - Scheduler activities
- Flask logs to console

## 🤝 Integration with Existing Dashboard

The Python API is compatible with the existing TypeScript/React dashboard. Simply update the API endpoints in your frontend to point to the Python API:

```typescript
// In your React components
const API_BASE = 'http://localhost:5000/api';
```

## 📞 Support

For issues or questions:
1. Check the logs
2. Review configuration
3. Test individual components
4. Verify database connectivity

## 🎯 Next Steps

1. **Production Deployment**: Use gunicorn or waitress for Flask API
2. **Docker Support**: Containerize the monitoring solution
3. **Advanced Alerts**: Add Slack, Teams, or PagerDuty integration
4. **Custom Dashboards**: Build Grafana dashboards
5. **Machine Learning**: Add predictive analytics

## 📄 License

Made with Bob - SQL Server Monitoring Dashboard

---

**Version**: 1.0.0  
**Last Updated**: 2026-06-14  
**Location**: C:\Users\00670T744\Videos\Python_SQLDBA