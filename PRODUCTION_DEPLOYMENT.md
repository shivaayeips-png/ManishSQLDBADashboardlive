# SQL Server Monitoring Dashboard - Production Deployment Guide

## 🚀 Production Deployment Steps

### Prerequisites
- Windows Server (2016 or later recommended)
- Python 3.8+ installed
- SQL Server with monitoring database created
- Network access to all target SQL Servers
- Service account with appropriate SQL Server permissions

---

## Step 1: Prepare Production Server

### 1.1 Install Python Dependencies
```powershell
# Navigate to application directory
cd C:\SQLMonitoring

# Install required packages
pip install flask pyodbc schedule
```

### 1.2 Create Application Directory Structure
```
C:\SQLMonitoring\
├── collect_sql_metrics.py
├── dashboard_api.py
├── customer_monitoring.py
├── alert_system.py
├── scheduler.py
├── monitoring_config.json
├── customer_dashboard_v2.html
├── logs\
└── sql\
```

---

## Step 2: Configure for Production

### 2.1 Update monitoring_config.json
```json
{
  "monitoring_server": {
    "server": "PROD-SQL-MONITOR\\INSTANCE",
    "database": "SQLServerMonitoring",
    "use_windows_auth": true,
    "username": "",
    "password": ""
  },
  "target_servers": [
    "PROD-SQL-01\\INSTANCE1",
    "PROD-SQL-02\\INSTANCE1",
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
    "enabled": true,
    "smtp_server": "smtp.company.com",
    "smtp_port": 587,
    "from_email": "sqlmonitoring@company.com",
    "to_emails": ["dba-team@company.com"],
    "username": "sqlmonitoring@company.com",
    "password": "your-email-password"
  }
}
```

### 2.2 Update dashboard_api.py for Production
Change the host and port:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
```

---

## Step 3: Set Up Windows Services

### 3.1 Create Monitoring Service Script
Create `run_monitoring_service.py`:
```python
import time
import logging
from datetime import datetime
import subprocess
import sys

logging.basicConfig(
    filename='C:\\SQLMonitoring\\logs\\service.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_monitoring():
    while True:
        try:
            logging.info("Starting monitoring collection...")
            subprocess.run([sys.executable, "C:\\SQLMonitoring\\collect_sql_metrics.py"], 
                         check=True)
            logging.info("Monitoring collection completed")
            time.sleep(60)  # Run every 60 seconds
        except Exception as e:
            logging.error(f"Error in monitoring: {e}")
            time.sleep(60)

if __name__ == '__main__':
    run_monitoring()
```

### 3.2 Install NSSM (Non-Sucking Service Manager)
```powershell
# Download NSSM from https://nssm.cc/download
# Extract to C:\nssm\

# Install Monitoring Service
C:\nssm\nssm.exe install SQLMonitoring "C:\Python39\python.exe" "C:\SQLMonitoring\run_monitoring_service.py"
C:\nssm\nssm.exe set SQLMonitoring AppDirectory "C:\SQLMonitoring"
C:\nssm\nssm.exe set SQLMonitoring DisplayName "SQL Server Monitoring Service"
C:\nssm\nssm.exe set SQLMonitoring Description "Collects SQL Server metrics for monitoring dashboard"
C:\nssm\nssm.exe set SQLMonitoring Start SERVICE_AUTO_START

# Install Dashboard API Service
C:\nssm\nssm.exe install SQLMonitoringAPI "C:\Python39\python.exe" "C:\SQLMonitoring\dashboard_api.py"
C:\nssm\nssm.exe set SQLMonitoringAPI AppDirectory "C:\SQLMonitoring"
C:\nssm\nssm.exe set SQLMonitoringAPI DisplayName "SQL Monitoring Dashboard API"
C:\nssm\nssm.exe set SQLMonitoringAPI Description "API service for SQL Server monitoring dashboard"
C:\nssm\nssm.exe set SQLMonitoringAPI Start SERVICE_AUTO_START

# Start Services
net start SQLMonitoring
net start SQLMonitoringAPI
```

---

## Step 4: Configure IIS (Optional - for better web hosting)

### 4.1 Install IIS with URL Rewrite
```powershell
# Install IIS
Install-WindowsFeature -name Web-Server -IncludeManagementTools

# Install URL Rewrite Module
# Download from: https://www.iis.net/downloads/microsoft/url-rewrite
```

### 4.2 Create IIS Site
1. Open IIS Manager
2. Create new site: "SQLMonitoringDashboard"
3. Physical path: `C:\SQLMonitoring\`
4. Binding: Port 80 or 443 (HTTPS)
5. Add `customer_dashboard_v2.html` as default document

### 4.3 Configure Reverse Proxy for API
Create `web.config` in `C:\SQLMonitoring\`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="API Proxy" stopProcessing="true">
                    <match url="^api/(.*)" />
                    <action type="Rewrite" url="http://localhost:8080/api/{R:1}" />
                </rule>
            </rules>
        </rewrite>
    </system.webServer>
</configuration>
```

---

## Step 5: Security Configuration

### 5.1 SQL Server Permissions
Create a dedicated service account with minimum permissions:
```sql
-- On monitoring database server
USE SQLServerMonitoring;
CREATE LOGIN [DOMAIN\SQLMonitoringSvc] FROM WINDOWS;
CREATE USER [DOMAIN\SQLMonitoringSvc] FOR LOGIN [DOMAIN\SQLMonitoringSvc];
ALTER ROLE db_datareader ADD MEMBER [DOMAIN\SQLMonitoringSvc];
ALTER ROLE db_datawriter ADD MEMBER [DOMAIN\SQLMonitoringSvc];
GRANT EXECUTE TO [DOMAIN\SQLMonitoringSvc];

-- On each target server
CREATE LOGIN [DOMAIN\SQLMonitoringSvc] FROM WINDOWS;
GRANT VIEW SERVER STATE TO [DOMAIN\SQLMonitoringSvc];
GRANT VIEW ANY DATABASE TO [DOMAIN\SQLMonitoringSvc];
```

### 5.2 Firewall Rules
```powershell
# Allow API port
New-NetFirewallRule -DisplayName "SQL Monitoring API" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow

# Allow HTTP/HTTPS (if using IIS)
New-NetFirewallRule -DisplayName "SQL Monitoring Dashboard HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "SQL Monitoring Dashboard HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
```

### 5.3 SSL Certificate (for HTTPS)
```powershell
# Generate self-signed certificate (for testing)
New-SelfSignedCertificate -DnsName "sqlmonitoring.company.com" -CertStoreLocation "cert:\LocalMachine\My"

# For production, use a proper SSL certificate from your CA
```

---

## Step 6: Monitoring and Maintenance

### 6.1 Set Up Log Rotation
Create `rotate_logs.ps1`:
```powershell
$logPath = "C:\SQLMonitoring\logs"
$maxAge = 30 # days

Get-ChildItem -Path $logPath -Filter "*.log" | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$maxAge) } | 
    Remove-Item -Force
```

Schedule with Task Scheduler to run daily.

### 6.2 Health Check Script
Create `health_check.ps1`:
```powershell
# Check if services are running
$services = @("SQLMonitoring", "SQLMonitoringAPI")
foreach ($service in $services) {
    $status = Get-Service -Name $service -ErrorAction SilentlyContinue
    if ($status.Status -ne "Running") {
        Write-Host "WARNING: $service is not running!"
        Start-Service -Name $service
    }
}

# Check API endpoint
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/api/monitoring/dashboard" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "API is healthy"
    }
} catch {
    Write-Host "ERROR: API is not responding"
}
```

---

## Step 7: Access the Dashboard

### Production URLs:
- **Dashboard**: `http://your-server-name/customer_dashboard_v2.html`
- **API**: `http://your-server-name:8080/api/monitoring/dashboard`
- **With IIS**: `http://sqlmonitoring.company.com`

### Network Access:
Ensure users can access the server on the configured ports (80/443 for web, 8080 for API).

---

## Step 8: Backup and Disaster Recovery

### 8.1 Backup Monitoring Database
```sql
-- Schedule daily backups
BACKUP DATABASE SQLServerMonitoring 
TO DISK = 'E:\Backups\SQLServerMonitoring_Full.bak'
WITH INIT, COMPRESSION;
```

### 8.2 Backup Configuration Files
```powershell
# Create backup script
$source = "C:\SQLMonitoring"
$destination = "\\backup-server\SQLMonitoring\$(Get-Date -Format 'yyyyMMdd')"
Copy-Item -Path $source -Destination $destination -Recurse -Force
```

---

## Troubleshooting

### Service Won't Start
```powershell
# Check service logs
Get-EventLog -LogName Application -Source "SQLMonitoring" -Newest 50

# Check Python errors
Get-Content C:\SQLMonitoring\logs\service.log -Tail 50
```

### Dashboard Not Loading
1. Check if API service is running: `Get-Service SQLMonitoringAPI`
2. Test API endpoint: `Invoke-WebRequest http://localhost:8080/api/monitoring/dashboard`
3. Check firewall rules
4. Verify IIS configuration

### No Data Showing
1. Check if monitoring service is running
2. Verify SQL Server connectivity
3. Check service account permissions
4. Review monitoring logs: `C:\SQLMonitoring\logs\`

---

## Performance Tuning

### For Large Environments (50+ servers):
1. Increase collection interval to 120-300 seconds
2. Implement data retention policy (keep 30-90 days)
3. Add database indexes on frequently queried columns
4. Consider separate monitoring servers for different regions

### Database Maintenance:
```sql
-- Clean old data (keep last 90 days)
DELETE FROM ServerMetrics WHERE CollectionTime < DATEADD(DAY, -90, GETDATE());
DELETE FROM DatabaseMetrics WHERE CollectionTime < DATEADD(DAY, -90, GETDATE());

-- Rebuild indexes weekly
ALTER INDEX ALL ON ServerMetrics REBUILD;
ALTER INDEX ALL ON DatabaseMetrics REBUILD;
```

---

## Support and Maintenance

### Regular Tasks:
- **Daily**: Check service status, review alerts
- **Weekly**: Review logs, check disk space
- **Monthly**: Update Python packages, review performance
- **Quarterly**: Review and update alert thresholds

### Monitoring the Monitor:
Set up external monitoring to ensure the monitoring system itself is healthy:
- Ping test to server
- HTTP check on dashboard URL
- Service status checks
- Database connectivity tests

---

## Success Checklist

- [ ] Python and dependencies installed
- [ ] Monitoring database created and configured
- [ ] All target servers added to config
- [ ] Windows services installed and running
- [ ] Dashboard accessible from network
- [ ] API responding correctly
- [ ] Alerts configured and tested
- [ ] Firewall rules configured
- [ ] SSL certificate installed (if using HTTPS)
- [ ] Backup procedures in place
- [ ] Documentation updated with your environment details
- [ ] Team trained on using the dashboard

---

**Your SQL Server Monitoring Dashboard is now production-ready! 🎉**