# 🚀 Step-by-Step Production Deployment Guide
## SQL Server Monitoring Dashboard

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- [ ] Windows Server (2016 or later) with admin access
- [ ] SQL Server instance for monitoring database
- [ ] Python 3.8+ installed on the server
- [ ] Network access to all SQL Servers you want to monitor
- [ ] Service account with SQL Server permissions

---

## STEP 1: Prepare Production Server

### 1.1 Install Python (if not already installed)

```powershell
# Download Python from python.org
# Or use Chocolatey:
choco install python -y

# Verify installation
python --version
```

### 1.2 Create Application Directory

```powershell
# Create main directory
New-Item -Path "C:\SQLMonitoring" -ItemType Directory -Force

# Create subdirectories
New-Item -Path "C:\SQLMonitoring\logs" -ItemType Directory -Force
New-Item -Path "C:\SQLMonitoring\sql" -ItemType Directory -Force
```

### 1.3 Install Python Dependencies

```powershell
cd C:\SQLMonitoring

# Install required packages
pip install flask pyodbc schedule
```

**✅ Checkpoint:** Python and dependencies installed

---

## STEP 2: Copy Project Files to Production Server

### 2.1 Copy Files from Your Development Machine

Copy these files from `c:\Users\00670T744\Videos\Python_SQLDBA\` to `C:\SQLMonitoring\`:

**Required Files:**
```
C:\SQLMonitoring\
├── collect_sql_metrics.py
├── dashboard_api.py
├── customer_monitoring.py
├── alert_system.py
├── scheduler.py
├── monitoring_config.json
├── customer_dashboard_v2.html
└── sql\
    └── Create-CustomerTables.sql
```

**Copy Command (from your dev machine):**
```powershell
# Option 1: Copy to network share
Copy-Item "c:\Users\00670T744\Videos\Python_SQLDBA\*" -Destination "\\PROD-SERVER\C$\SQLMonitoring\" -Recurse

# Option 2: Use USB drive or shared folder
# Copy files manually to production server
```

**✅ Checkpoint:** All files copied to production server

---

## STEP 3: Create Monitoring Database on Production SQL Server

### 3.1 Connect to Production SQL Server

```powershell
# Open SQL Server Management Studio (SSMS)
# Connect to your production SQL Server instance
```

### 3.2 Create Monitoring Database

```sql
-- Run this in SSMS on production SQL Server
CREATE DATABASE SQLServerMonitoring;
GO

USE SQLServerMonitoring;
GO
```

### 3.3 Create Tables and Stored Procedures

```sql
-- Copy and run the entire Create-CustomerTables.sql script
-- Location: C:\SQLMonitoring\sql\Create-CustomerTables.sql

-- Or run from command line:
sqlcmd -S YOUR-PROD-SERVER\INSTANCE -d SQLServerMonitoring -i "C:\SQLMonitoring\sql\Create-CustomerTables.sql"
```

**✅ Checkpoint:** Monitoring database created with all tables

---

## STEP 4: Configure Production Settings

### 4.1 Update monitoring_config.json

Edit `C:\SQLMonitoring\monitoring_config.json`:

```json
{
  "monitoring_server": {
    "server": "PROD-SQL-01\\INSTANCE",
    "database": "SQLServerMonitoring",
    "use_windows_auth": true,
    "username": "",
    "password": ""
  },
  "target_servers": [
    "PROD-SQL-01\\INSTANCE",
    "PROD-SQL-02\\INSTANCE",
    "PROD-SQL-03",
    "PROD-SQL-04",
    "PROD-SQL-05"
  ],
  "collection_interval_seconds": 60,
  "alert_thresholds": {
    "cpu_percent": 80,
    "memory_percent": 85,
    "blocked_sessions": 5,
    "response_time_ms": 1000
  },
  "email_alerts": {
    "enabled": false,
    "smtp_server": "smtp.company.com",
    "smtp_port": 587,
    "from_email": "sqlmonitoring@company.com",
    "to_emails": ["dba-team@company.com"],
    "username": "",
    "password": ""
  }
}
```

**Replace:**
- `PROD-SQL-01\\INSTANCE` with your actual SQL Server name
- Add all your production SQL Servers to `target_servers` array

### 4.2 Update dashboard_api.py for Production

Edit `C:\SQLMonitoring\dashboard_api.py`, find the last line and change:

```python
# Change from:
app.run(host='127.0.0.1', port=7070, debug=True)

# To:
app.run(host='0.0.0.0', port=8080, debug=False)
```

**✅ Checkpoint:** Configuration files updated

---

## STEP 5: Set Up SQL Server Permissions

### 5.1 Create Service Account (if using Windows Auth)

```sql
-- Run on monitoring database server
USE SQLServerMonitoring;
GO

-- Create login for the Windows account that will run the service
-- Replace DOMAIN\ServiceAccount with your actual service account
CREATE LOGIN [DOMAIN\ServiceAccount] FROM WINDOWS;
CREATE USER [DOMAIN\ServiceAccount] FOR LOGIN [DOMAIN\ServiceAccount];

-- Grant permissions
ALTER ROLE db_datareader ADD MEMBER [DOMAIN\ServiceAccount];
ALTER ROLE db_datawriter ADD MEMBER [DOMAIN\ServiceAccount];
GRANT EXECUTE TO [DOMAIN\ServiceAccount];
GO
```

### 5.2 Grant Permissions on Target Servers

```sql
-- Run this on EACH target SQL Server you want to monitor
CREATE LOGIN [DOMAIN\ServiceAccount] FROM WINDOWS;
GRANT VIEW SERVER STATE TO [DOMAIN\ServiceAccount];
GRANT VIEW ANY DATABASE TO [DOMAIN\ServiceAccount];
GO
```

**✅ Checkpoint:** SQL Server permissions configured

---

## STEP 6: Test the Application Manually

### 6.1 Test Data Collection

```powershell
cd C:\SQLMonitoring

# Run monitoring script once
python collect_sql_metrics.py
```

**Expected Output:**
```
Collecting metrics from PROD-SQL-01...
Successfully collected metrics from PROD-SQL-01
Collecting metrics from PROD-SQL-02...
Successfully collected metrics from PROD-SQL-02
...
```

### 6.2 Test API Server

```powershell
# Start API server
python dashboard_api.py
```

**Expected Output:**
```
* Running on http://0.0.0.0:8080
```

### 6.3 Test Dashboard Access

Open browser and navigate to:
```
http://localhost:8080/customer_dashboard_v2.html
```

**You should see:**
- Server health metrics
- Database counts
- CPU usage
- Active connections

**✅ Checkpoint:** Application working manually

---

## STEP 7: Install as Windows Service

### 7.1 Download and Install NSSM

```powershell
# Download NSSM from https://nssm.cc/download
# Extract to C:\nssm\

# Or use Chocolatey:
choco install nssm -y
```

### 7.2 Create Monitoring Service

```powershell
# Install monitoring collection service
nssm install SQLMonitoring "C:\Python39\python.exe" "C:\SQLMonitoring\collect_sql_metrics.py"

# Configure service
nssm set SQLMonitoring AppDirectory "C:\SQLMonitoring"
nssm set SQLMonitoring DisplayName "SQL Server Monitoring - Data Collection"
nssm set SQLMonitoring Description "Collects metrics from SQL Servers every 60 seconds"
nssm set SQLMonitoring Start SERVICE_AUTO_START
nssm set SQLMonitoring AppStdout "C:\SQLMonitoring\logs\monitoring.log"
nssm set SQLMonitoring AppStderr "C:\SQLMonitoring\logs\monitoring_error.log"
```

### 7.3 Create API Service

```powershell
# Install API service
nssm install SQLMonitoringAPI "C:\Python39\python.exe" "C:\SQLMonitoring\dashboard_api.py"

# Configure service
nssm set SQLMonitoringAPI AppDirectory "C:\SQLMonitoring"
nssm set SQLMonitoringAPI DisplayName "SQL Server Monitoring - Dashboard API"
nssm set SQLMonitoringAPI Description "API service for monitoring dashboard"
nssm set SQLMonitoringAPI Start SERVICE_AUTO_START
nssm set SQLMonitoringAPI AppStdout "C:\SQLMonitoring\logs\api.log"
nssm set SQLMonitoringAPI AppStderr "C:\SQLMonitoring\logs\api_error.log"
```

### 7.4 Start Services

```powershell
# Start both services
net start SQLMonitoring
net start SQLMonitoringAPI

# Verify services are running
Get-Service SQLMonitoring, SQLMonitoringAPI
```

**Expected Output:**
```
Status   Name               DisplayName
------   ----               -----------
Running  SQLMonitoring      SQL Server Monitoring - Data Collection
Running  SQLMonitoringAPI   SQL Server Monitoring - Dashboard API
```

**✅ Checkpoint:** Services installed and running

---

## STEP 8: Configure Firewall

### 8.1 Open Required Ports

```powershell
# Allow API port (8080)
New-NetFirewallRule -DisplayName "SQL Monitoring API" `
    -Direction Inbound `
    -LocalPort 8080 `
    -Protocol TCP `
    -Action Allow

# Verify rule created
Get-NetFirewallRule -DisplayName "SQL Monitoring API"
```

**✅ Checkpoint:** Firewall configured

---

## STEP 9: Access Dashboard from Network

### 9.1 Find Server IP Address

```powershell
# Get server IP address
ipconfig | findstr IPv4
```

**Example Output:**
```
IPv4 Address. . . . . . . . . . . : 192.168.1.100
```

### 9.2 Access Dashboard

From any computer on your network, open browser:
```
http://192.168.1.100:8080/customer_dashboard_v2.html
```

**Or use server name:**
```
http://PROD-SERVER:8080/customer_dashboard_v2.html
```

**✅ Checkpoint:** Dashboard accessible from network

---

## STEP 10: Verify Everything is Working

### 10.1 Check Services

```powershell
# Check service status
Get-Service SQLMonitoring, SQLMonitoringAPI | Format-Table -AutoSize

# Check service logs
Get-Content C:\SQLMonitoring\logs\monitoring.log -Tail 20
Get-Content C:\SQLMonitoring\logs\api.log -Tail 20
```

### 10.2 Check Database

```sql
-- Connect to monitoring database
USE SQLServerMonitoring;

-- Check recent data
SELECT TOP 10 * FROM ServerMetrics ORDER BY CollectionTime DESC;
SELECT TOP 10 * FROM DatabaseMetrics ORDER BY CollectionTime DESC;

-- Check server count
SELECT COUNT(DISTINCT ServerName) AS TotalServers FROM ServerMetrics;
```

### 10.3 Check Dashboard

Open dashboard and verify:
- [ ] Server Health shows correct number of servers
- [ ] Database count is accurate
- [ ] CPU usage is displaying
- [ ] Active connections showing
- [ ] Data refreshes automatically

**✅ Checkpoint:** Everything verified and working!

---

## STEP 11: Set Up Monitoring Schedule (Optional)

### 11.1 Create Scheduled Task for Data Cleanup

```powershell
# Create cleanup script
$cleanupScript = @'
# Clean old data (keep last 90 days)
$connectionString = "Server=PROD-SQL-01\INSTANCE;Database=SQLServerMonitoring;Integrated Security=True;"
$connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
$connection.Open()

$command = $connection.CreateCommand()
$command.CommandText = @"
DELETE FROM ServerMetrics WHERE CollectionTime < DATEADD(DAY, -90, GETDATE());
DELETE FROM DatabaseMetrics WHERE CollectionTime < DATEADD(DAY, -90, GETDATE());
"@
$command.ExecuteNonQuery()
$connection.Close()

Write-Host "Cleanup completed: $(Get-Date)"
'@

$cleanupScript | Out-File "C:\SQLMonitoring\cleanup_old_data.ps1"

# Schedule to run weekly
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\SQLMonitoring\cleanup_old_data.ps1"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am
Register-ScheduledTask -TaskName "SQLMonitoring-Cleanup" -Action $action -Trigger $trigger -RunLevel Highest
```

**✅ Checkpoint:** Maintenance scheduled

---

## STEP 12: Document Your Deployment

### 12.1 Create Documentation

Create a file `C:\SQLMonitoring\DEPLOYMENT_INFO.txt`:

```
SQL Server Monitoring Dashboard - Production Deployment
========================================================

Deployment Date: [TODAY'S DATE]
Deployed By: [YOUR NAME]

Server Details:
- Production Server: [SERVER NAME]
- Monitoring Database: [SERVER\INSTANCE]
- Dashboard URL: http://[SERVER-IP]:8080/customer_dashboard_v2.html

Monitored SQL Servers:
1. [SERVER1\INSTANCE]
2. [SERVER2\INSTANCE]
3. [SERVER3]
...

Service Account: [DOMAIN\ServiceAccount]

Services:
- SQLMonitoring (Data Collection)
- SQLMonitoringAPI (Dashboard API)

Maintenance:
- Data retention: 90 days
- Cleanup schedule: Weekly (Sunday 2 AM)

Contact: [YOUR EMAIL]
```

**✅ Checkpoint:** Deployment documented

---

## 🎉 DEPLOYMENT COMPLETE!

### Your Dashboard is Now Live!

**Access URLs:**
- Internal: `http://[SERVER-NAME]:8080/customer_dashboard_v2.html`
- IP Address: `http://[SERVER-IP]:8080/customer_dashboard_v2.html`

### What's Running:
✅ Monitoring service collecting data every 60 seconds
✅ API service serving dashboard 24/7
✅ Auto-starts with server reboot
✅ Monitoring all configured SQL Servers

---

## 📞 Troubleshooting

### Services Not Starting?
```powershell
# Check service status
Get-Service SQLMonitoring, SQLMonitoringAPI

# Check logs
Get-Content C:\SQLMonitoring\logs\monitoring_error.log
Get-Content C:\SQLMonitoring\logs\api_error.log

# Restart services
Restart-Service SQLMonitoring, SQLMonitoringAPI
```

### Dashboard Not Loading?
1. Check if API service is running
2. Test API: `http://localhost:8080/api/monitoring/dashboard`
3. Check firewall rules
4. Verify port 8080 is not blocked

### No Data Showing?
1. Check monitoring service logs
2. Verify SQL Server connectivity
3. Check service account permissions
4. Run `collect_sql_metrics.py` manually to see errors

---

## 📊 Next Steps

1. **Share with Team**: Send dashboard URL to your team
2. **Set Up Alerts**: Enable email alerts in config
3. **Add More Servers**: Update `target_servers` in config
4. **Monitor Performance**: Check logs regularly
5. **Plan Maintenance**: Schedule regular reviews

---

## 🔒 Security Checklist

- [ ] Service account has minimum required permissions
- [ ] Firewall rules configured
- [ ] Dashboard accessible only from internal network
- [ ] Monitoring database backed up regularly
- [ ] Service logs reviewed weekly

---

**Congratulations! Your SQL Server Monitoring Dashboard is now in production! 🚀**