# Customer-Based SQL Server Monitoring Guide

## 🎯 Overview

This guide explains how to use the customer-based monitoring system that allows you to select from **Top 10 Customers** and check their **Server Availability** and **Database Availability** through a dropdown interface.

## 📋 Features

✅ **Customer Dropdown Selection** - Choose from Top 10 customers  
✅ **Server Availability Monitoring** - Real-time server status for each customer  
✅ **Database Availability Monitoring** - Track all databases per customer  
✅ **Priority-Based Organization** - Critical, High, Medium, Low priorities  
✅ **Interactive Dashboard** - Beautiful web interface with live data  
✅ **REST API Endpoints** - Programmatic access to customer data  
✅ **Python Monitoring Script** - Automated monitoring per customer  

## 🚀 Quick Start

### 1. Setup Database Tables

First, create the customer tables in your monitoring database:

```bash
sqlcmd -S your-server-name -d SQLServerMonitoring -i sql/Create-CustomerTables.sql
```

Or using PowerShell:

```powershell
Invoke-Sqlcmd -ServerInstance "your-server-name" -Database "SQLServerMonitoring" -InputFile "sql/Create-CustomerTables.sql"
```

This creates:
- **Customers** table (Top 10 customers with priority levels)
- **CustomerServers** table (Server mappings for each customer)
- **Views** for easy querying
- **Stored Procedures** for data retrieval

### 2. Configure Customer Data

Edit `customer_config.json` to match your actual customer servers:

```json
{
  "customers": [
    {
      "customer_id": 1,
      "customer_name": "Acme Corporation",
      "servers": [
        {
          "server_name": "ACME-SQL-PROD-01",
          "server_instance": "ACME-SQL-PROD-01\\PRODUCTION",
          "description": "Primary Production Server"
        }
      ],
      "priority": "High",
      "contact_email": "dba@acmecorp.com"
    }
  ]
}
```

### 3. Start the API Server

```bash
python dashboard_api.py
```

The API will be available at `http://localhost:5000`

### 4. Open the Dashboard

Open `customer_dashboard.html` in your web browser:

```bash
# Windows
start customer_dashboard.html

# Or just double-click the file
```

## 📊 Using the Dashboard

### Customer Selection

1. **Open the Dashboard** - Load `customer_dashboard.html` in your browser
2. **Select Customer** - Choose from the dropdown (shows all Top 10 customers)
3. **View Status** - Automatically loads server and database availability
4. **Refresh Data** - Click the refresh button to get latest status

### Dashboard Sections

#### 1. Customer Information Panel
- Customer Name
- Priority Level (Critical/High/Medium/Low)
- Total Servers
- Available Servers
- Total Databases
- Online Databases

#### 2. Server Availability Section
Shows for each server:
- Server Name and Instance
- Online/Offline Status
- Response Time (ms)
- CPU Usage (%)
- Memory Usage (%)
- Active Connections
- Online Database Count

#### 3. Database Availability Section
Table showing:
- Server Name
- Database Name
- Status (ONLINE/OFFLINE)
- Recovery Model
- Size (MB)
- Compatibility Level

## 🔌 API Endpoints

### Get All Customers

```http
GET /api/monitoring/customers
```

**Response:**
```json
{
  "customers": [
    {
      "customer_id": 1,
      "customer_name": "Acme Corporation",
      "priority": "High",
      "server_count": 2,
      "contact_email": "dba@acmecorp.com"
    }
  ],
  "total": 10
}
```

### Get Customer Details

```http
GET /api/monitoring/customers/{customer_id}
```

**Example:**
```http
GET /api/monitoring/customers/1
```

**Response:**
```json
{
  "customer_id": 1,
  "customer_name": "Acme Corporation",
  "priority": "High",
  "servers": [
    {
      "server_name": "ACME-SQL-PROD-01",
      "server_instance": "ACME-SQL-PROD-01\\PRODUCTION",
      "description": "Primary Production Server"
    }
  ],
  "contact_email": "dba@acmecorp.com"
}
```

### Get Customer Status (Real-time)

```http
GET /api/monitoring/customers/{customer_id}/status
```

**Example:**
```http
GET /api/monitoring/customers/1/status
```

**Response:**
```json
{
  "customer_id": 1,
  "customer_name": "Acme Corporation",
  "priority": "High",
  "servers": [
    {
      "ServerName": "ACME-SQL-PROD-01\\PRODUCTION",
      "IsAvailable": true,
      "ResponseTimeMs": 45.5,
      "CPUUsagePercent": 35.2,
      "MemoryUsagePercent": 65.8,
      "ActiveConnections": 15,
      "OnlineDatabaseCount": 7
    }
  ],
  "databases": [
    {
      "ServerName": "ACME-SQL-PROD-01\\PRODUCTION",
      "DatabaseName": "ProductionDB",
      "State": "ONLINE",
      "RecoveryModel": "FULL",
      "SizeMB": 1024.5,
      "CompatibilityLevel": 150
    }
  ],
  "summary": {
    "total_servers": 2,
    "available_servers": 2,
    "total_databases": 7,
    "online_databases": 7
  },
  "timestamp": "2026-06-15T16:50:00.000Z"
}
```

## 🐍 Python Monitoring Script

### Interactive Mode

Run the customer monitoring script:

```bash
python customer_monitoring.py
```

**Menu Options:**
- Enter **1-10** to monitor a specific customer
- Enter **all** to monitor all customers
- Enter **exit** to quit

### Example Session

```
TOP 10 CUSTOMERS
================================================================================
 1. Acme Corporation              | Priority: High     | Servers: 2
 2. TechVision Inc                | Priority: High     | Servers: 1
 3. Global Finance Ltd            | Priority: Critical | Servers: 2
 4. HealthCare Systems            | Priority: Critical | Servers: 1
 5. RetailMax Group               | Priority: High     | Servers: 2
 6. Manufacturing Pro             | Priority: Medium   | Servers: 1
 7. Education Portal              | Priority: Medium   | Servers: 1
 8. Logistics Express             | Priority: High     | Servers: 2
 9. Media Solutions               | Priority: Medium   | Servers: 1
10. Insurance Partners            | Priority: Critical | Servers: 2
================================================================================

Customer ID: 1

============================================================
Monitoring Customer: Acme Corporation
Priority: High
Contact: dba@acmecorp.com
============================================================

Checking server: ACME-SQL-PROD-01 (Primary Production Server)
✓ [Acme Corporation] Server ACME-SQL-PROD-01\PRODUCTION is ONLINE (Response: 45.5ms)
  [Acme Corporation] Found 7 databases (7 online)

============================================================
Summary for Acme Corporation:
  Servers: 2/2 available
  Databases: 7/7 online
============================================================
```

### Programmatic Usage

```python
from customer_monitoring import CustomerMonitor

# Initialize monitor
monitor = CustomerMonitor()

# Get top 10 customers
customers = monitor.get_top_customers()

# Monitor specific customer
results = monitor.monitor_customer(customer_id=1)

# Save results to database
monitor.save_customer_monitoring_results(results)
```

## 📁 File Structure

```
Python_SQLDBA/
├── customer_config.json              # Customer configuration
├── customer_monitoring.py            # Python monitoring script
├── customer_dashboard.html           # Web dashboard
├── dashboard_api.py                  # Updated API with customer endpoints
├── sql/
│   └── Create-CustomerTables.sql    # Database setup script
└── CUSTOMER_MONITORING_GUIDE.md     # This guide
```

## 🎨 Top 10 Customers

The system comes pre-configured with 10 sample customers:

| # | Customer Name | Priority | Servers |
|---|---------------|----------|---------|
| 1 | Acme Corporation | High | 2 |
| 2 | TechVision Inc | High | 1 |
| 3 | Global Finance Ltd | Critical | 2 |
| 4 | HealthCare Systems | Critical | 1 |
| 5 | RetailMax Group | High | 2 |
| 6 | Manufacturing Pro | Medium | 1 |
| 7 | Education Portal | Medium | 1 |
| 8 | Logistics Express | High | 2 |
| 9 | Media Solutions | Medium | 1 |
| 10 | Insurance Partners | Critical | 2 |

## 🔧 Configuration

### Adding New Customers

#### Option 1: Update JSON Configuration

Edit `customer_config.json`:

```json
{
  "customer_id": 11,
  "customer_name": "New Customer Inc",
  "servers": [
    {
      "server_name": "NEW-SQL-01",
      "server_instance": "NEW-SQL-01\\INSTANCE1",
      "description": "Main Server"
    }
  ],
  "priority": "High",
  "contact_email": "admin@newcustomer.com"
}
```

#### Option 2: Add to Database

```sql
-- Add customer
INSERT INTO Customers (CustomerName, Priority, ContactEmail)
VALUES ('New Customer Inc', 'High', 'admin@newcustomer.com');

-- Get the new CustomerID
DECLARE @CustomerID INT = SCOPE_IDENTITY();

-- Add server mapping
INSERT INTO CustomerServers (CustomerID, ServerName, ServerInstance, Description)
VALUES (@CustomerID, 'NEW-SQL-01', 'NEW-SQL-01\INSTANCE1', 'Main Server');
```

### Updating Server Mappings

```sql
-- Update server instance
UPDATE CustomerServers
SET ServerInstance = 'NEW-SERVER-NAME\INSTANCE'
WHERE CustomerID = 1 AND ServerName = 'OLD-SERVER-NAME';

-- Add new server to existing customer
INSERT INTO CustomerServers (CustomerID, ServerName, ServerInstance, Description)
VALUES (1, 'NEW-SERVER', 'NEW-SERVER\INSTANCE', 'Additional Server');
```

## 📊 Database Queries

### Get Customer Summary

```sql
EXEC sp_GetAllCustomersSummary;
```

### Get Specific Customer Status

```sql
EXEC sp_GetCustomerStatus @CustomerID = 1;
```

### View Current Status

```sql
SELECT * FROM vw_CustomerServerStatus
WHERE CustomerName = 'Acme Corporation';
```

### Find Offline Servers

```sql
SELECT 
    CustomerName,
    ServerName,
    ServerInstance,
    CheckTime
FROM vw_CustomerServerStatus
WHERE IsAvailable = 0
ORDER BY Priority, CustomerName;
```

### Find Offline Databases

```sql
SELECT 
    c.CustomerName,
    cs.ServerInstance,
    da.DatabaseName,
    da.State,
    da.CheckTime
FROM Customers c
INNER JOIN CustomerServers cs ON c.CustomerID = cs.CustomerID
INNER JOIN DatabaseAvailability da ON cs.ServerInstance = da.ServerName
WHERE da.State <> 'ONLINE'
AND da.CheckTime = (SELECT MAX(CheckTime) FROM DatabaseAvailability WHERE ServerName = cs.ServerInstance)
ORDER BY c.Priority, c.CustomerName;
```

## 🔍 Troubleshooting

### Dashboard Not Loading Customers

1. **Check API is running:**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Verify customer endpoint:**
   ```bash
   curl http://localhost:5000/api/monitoring/customers
   ```

3. **Check browser console** for JavaScript errors

### No Data Showing for Customer

1. **Verify customer exists in database:**
   ```sql
   SELECT * FROM Customers WHERE CustomerID = 1;
   ```

2. **Check server mappings:**
   ```sql
   SELECT * FROM CustomerServers WHERE CustomerID = 1;
   ```

3. **Verify monitoring data exists:**
   ```sql
   SELECT TOP 10 * FROM ServerAvailability ORDER BY CheckTime DESC;
   ```

### Python Script Connection Issues

1. **Test database connection:**
   ```python
   import pyodbc
   conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=your-server;DATABASE=SQLServerMonitoring;Trusted_Connection=yes;")
   print("Connected successfully!")
   ```

2. **Check customer config file:**
   ```bash
   python -c "import json; print(json.load(open('customer_config.json')))"
   ```

3. **Review logs:**
   ```bash
   type customer_monitoring.log
   ```

## 🎯 Best Practices

### 1. Regular Monitoring

Set up scheduled monitoring for each customer:

```bash
# Windows Task Scheduler
# Run every 30 minutes for all customers
python customer_monitoring.py --customer all --save-results
```

### 2. Priority-Based Alerts

Configure different alert thresholds based on customer priority:

```json
{
  "alert_thresholds": {
    "Critical": {
      "cpu_percent": 70,
      "memory_percent": 75,
      "response_time_ms": 500
    },
    "High": {
      "cpu_percent": 80,
      "memory_percent": 85,
      "response_time_ms": 1000
    },
    "Medium": {
      "cpu_percent": 90,
      "memory_percent": 90,
      "response_time_ms": 2000
    }
  }
}
```

### 3. Data Retention

Clean old monitoring data regularly:

```sql
-- Keep last 30 days for Critical customers
DELETE FROM ServerAvailability 
WHERE CheckTime < DATEADD(DAY, -30, GETDATE())
AND ServerName IN (
    SELECT cs.ServerInstance 
    FROM CustomerServers cs
    INNER JOIN Customers c ON cs.CustomerID = c.CustomerID
    WHERE c.Priority = 'Critical'
);

-- Keep last 7 days for Medium/Low priority
DELETE FROM ServerAvailability 
WHERE CheckTime < DATEADD(DAY, -7, GETDATE())
AND ServerName IN (
    SELECT cs.ServerInstance 
    FROM CustomerServers cs
    INNER JOIN Customers c ON cs.CustomerID = c.CustomerID
    WHERE c.Priority IN ('Medium', 'Low')
);
```

## 📈 Advanced Usage

### Automated Reporting

Generate daily reports for each customer:

```python
from customer_monitoring import CustomerMonitor
import json
from datetime import datetime

monitor = CustomerMonitor()

# Generate report for all customers
report_date = datetime.now().strftime('%Y-%m-%d')
report = []

for customer in monitor.get_top_customers():
    results = monitor.monitor_customer(customer['customer_id'])
    report.append(results)

# Save report
with open(f'customer_report_{report_date}.json', 'w') as f:
    json.dump(report, f, indent=2)
```

### Integration with Alerting Systems

```python
def send_customer_alert(customer_name, server_name, issue):
    """Send alert for customer-specific issues"""
    # Integrate with your alerting system
    # Email, Slack, Teams, PagerDuty, etc.
    pass
```

## 📞 Support

For issues or questions:
1. Check the logs: `customer_monitoring.log`
2. Verify database connectivity
3. Test API endpoints
4. Review configuration files

## 🎉 Summary

You now have a complete customer-based monitoring system with:

✅ **Dropdown Selection** - Easy customer selection  
✅ **Real-time Monitoring** - Live server and database status  
✅ **Beautiful Dashboard** - Professional web interface  
✅ **REST API** - Programmatic access  
✅ **Python Scripts** - Automated monitoring  
✅ **Database Integration** - Persistent storage  
✅ **Priority Management** - Critical to Low priorities  

**Happy Monitoring!** 🚀📊

---

**Version:** 1.0.0  
**Last Updated:** 2026-06-15  
**Location:** C:\Users\00670T744\Videos\Python_SQLDBA