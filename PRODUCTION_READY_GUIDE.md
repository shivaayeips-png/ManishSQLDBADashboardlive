# 🚀 GXO SQL Server Monitoring - Production Ready Guide

## 📋 Overview

This guide provides complete instructions for deploying the GXO SQL Server Monitoring Dashboard in a production environment with proper customer and server filtering.

---

## ✨ What's New in Production Version

### Key Features:
1. ✅ **Customer-Based Filtering** - Select customer to view their servers
2. ✅ **Server-Specific Data** - View detailed metrics for selected server only
3. ✅ **Real-Time Updates** - Refresh button for latest data
4. ✅ **Production-Ready API** - New `/api/monitoring/server-details` endpoint
5. ✅ **Clean UI** - Professional dashboard with proper data isolation
6. ✅ **Error Handling** - Robust error messages and loading states

---

## 🎯 Quick Start

### Option 1: One-Click Launch (Recommended)

1. **Navigate to project folder:**
   ```
   C:\Users\00670T744\Videos\Python_SQLDBA
   ```

2. **Double-click:**
   ```
   START_PRODUCTION_DASHBOARD.bat
   ```

3. **Dashboard opens automatically at:**
   ```
   http://localhost:7070/monitoring
   ```

### Option 2: Manual Start

1. **Open Command Prompt**

2. **Navigate to project:**
   ```cmd
   cd C:\Users\00670T744\Videos\Python_SQLDBA
   ```

3. **Start API server:**
   ```cmd
   py dashboard_api.py
   ```

4. **Open browser and go to:**
   ```
   http://localhost:7070/monitoring
   ```

---

## 📊 How to Use the Dashboard

### Step 1: Select Customer
1. Click the **"Select Customer"** dropdown
2. Choose a customer (e.g., "Manish Genious" or "Apple")
3. The server dropdown will populate with that customer's servers

### Step 2: Select Server
1. Click the **"Select Server"** dropdown
2. Choose a server instance (e.g., "00670T\MANISHPREET")
3. Dashboard will load data for ONLY that server

### Step 3: View Metrics
The dashboard displays:
- **Server Status**: Online/Offline with response time
- **Total Databases**: Count with online/offline breakdown
- **CPU Usage**: Current CPU percentage
- **Memory Usage**: Current memory percentage
- **Server Details**: Response time, connections, blocked sessions, SQL version
- **Database List**: All databases on the selected server with status and size

### Step 4: Refresh Data
- Click the **"🔄 Refresh"** button to get latest data
- Last updated time is shown in the header

---

## 🔧 Configuration Files

### 1. customer_config.json
Defines customers and their servers:

```json
{
  "customers": [
    {
      "customer_id": 1,
      "customer_name": "Manish Genious",
      "servers": [
        {
          "server_name": "00670T\\MANISHPREET",
          "server_instance": "00670T\\MANISHPREET",
          "description": "Production SQL Server"
        }
      ],
      "priority": "Critical",
      "contact_email": "admin@production.local"
    },
    {
      "customer_id": 2,
      "customer_name": "Apple",
      "servers": [
        {
          "server_name": "preet",
          "server_instance": "preet",
          "description": "Apple Production SQL Server"
        }
      ],
      "priority": "High",
      "contact_email": "admin@apple.local"
    }
  ]
}
```

### 2. monitoring_config.json
Database connection settings:

```json
{
  "monitoring_server": {
    "server": "00670T\\MANISHPREET",
    "database": "SQLServerMonitoring",
    "use_windows_auth": false,
    "username": "manish",
    "password": "manish@79"
  },
  "collection_interval_seconds": 30,
  "alert_thresholds": {
    "cpu_percent": 80,
    "memory_percent": 85,
    "blocked_sessions": 5
  }
}
```

---

## 🌐 API Endpoints

### Production Endpoints:

#### 1. Get Customers List
```
GET http://localhost:7070/api/monitoring/customers?limit=0
```
Returns all customers with their server counts.

#### 2. Get Customer Details
```
GET http://localhost:7070/api/monitoring/customers/{customer_id}
```
Returns specific customer with server list.

#### 3. Get Server Details (NEW - Production Ready)
```
GET http://localhost:7070/api/monitoring/server-details?server={server_instance}
```
Returns complete server and database information for a specific server.

**Response Example:**
```json
{
  "server_name": "00670T\\MANISHPREET",
  "server_status": {
    "is_available": true,
    "response_time_ms": 539.2,
    "cpu_usage_percent": 35.5,
    "memory_usage_percent": 62.3,
    "active_connections": 7,
    "blocked_sessions": 0,
    "version": "Microsoft SQL Server 2019"
  },
  "database_summary": {
    "total_databases": 7,
    "online_databases": 7,
    "offline_databases": 0,
    "total_size_mb": 1024.5
  },
  "databases": [
    {
      "DatabaseName": "master",
      "State": "ONLINE",
      "SizeMB": 6.25,
      "RecoveryModel": "SIMPLE"
    }
  ],
  "timestamp": "2026-06-17T21:30:00.000Z"
}
```

#### 4. Get Dashboard Summary
```
GET http://localhost:7070/api/monitoring/dashboard
```
Returns overall system summary (all servers).

#### 5. Get Servers Status
```
GET http://localhost:7070/api/monitoring/servers?server={server_name}
```
Returns server availability and performance metrics.

#### 6. Get Databases Status
```
GET http://localhost:7070/api/monitoring/databases?server={server_name}
```
Returns database status for specific server.

---

## 🔐 Security Considerations for Production

### 1. Database Credentials
- Store credentials securely (use environment variables or Azure Key Vault)
- Don't commit `monitoring_config.json` to version control
- Use SQL Server authentication with strong passwords

### 2. API Security
- Add authentication middleware (JWT tokens)
- Implement rate limiting
- Use HTTPS in production
- Add CORS restrictions for specific domains

### 3. Network Security
- Run API behind a reverse proxy (IIS, Nginx)
- Use firewall rules to restrict access
- Enable SQL Server encryption

---

## 📁 File Structure

```
C:\Users\00670T744\Videos\Python_SQLDBA\
│
├── dashboard_api.py                    # Flask API server (UPDATED)
├── customer_dashboard_production.html  # Production dashboard (NEW)
├── START_PRODUCTION_DASHBOARD.bat      # One-click launcher (NEW)
├── PRODUCTION_READY_GUIDE.md          # This file (NEW)
│
├── customer_config.json               # Customer configuration
├── monitoring_config.json             # Database connection config
├── requirements.txt                   # Python dependencies
│
├── collect_sql_metrics.py            # Metrics collection script
├── customer_monitoring.py            # CLI monitoring tool
├── alert_system.py                   # Alert system
│
└── sql/
    ├── Create-CustomerTables.sql     # Database setup
    └── Fix-DatabaseCount.sql         # Database fixes
```

---

## 🐛 Troubleshooting

### Issue: Dashboard shows "Failed to load customers"
**Solution:**
1. Check if API server is running on port 7070
2. Verify `customer_config.json` exists and is valid JSON
3. Check browser console for errors (F12)

### Issue: Server data not loading
**Solution:**
1. Verify server name in `customer_config.json` matches actual SQL Server instance
2. Check SQL Server is running and accessible
3. Test connection: `sqlcmd -S 00670T744\MANISHPREET -U manish -P manish@79`

### Issue: Database list is empty
**Solution:**
1. Ensure monitoring data is being collected
2. Run: `py collect_sql_metrics.py` to populate data
3. Check `DatabaseStatus` table has data

### Issue: Port 7070 already in use
**Solution:**
1. Find process using port: `netstat -ano | findstr :7070`
2. Kill process: `taskkill /PID {process_id} /F`
3. Or change port in `dashboard_api.py` (line 519)

---

## 📈 Performance Optimization

### For Production:
1. **Enable caching** - Cache customer/server lists
2. **Database indexing** - Add indexes on ServerName, CheckTime columns
3. **Connection pooling** - Use pyodbc connection pooling
4. **Async operations** - Use async/await for API calls
5. **Data pagination** - Limit database list to recent entries

---

## 🔄 Maintenance

### Daily Tasks:
- Monitor API server logs
- Check disk space for log files
- Verify data collection is running

### Weekly Tasks:
- Review alert history
- Check database growth
- Update customer configurations if needed

### Monthly Tasks:
- Archive old monitoring data
- Review and optimize SQL queries
- Update Python dependencies

---

## 📞 Support

### Common Commands:

**Check API Status:**
```cmd
curl http://localhost:7070/api/health
```

**View Customers:**
```cmd
curl http://localhost:7070/api/monitoring/customers
```

**Test Server Details:**
```cmd
curl "http://localhost:7070/api/monitoring/server-details?server=00670T\\MANISHPREET"
```

---

## ✅ Production Checklist

Before deploying to production:

- [ ] Update `customer_config.json` with all customers
- [ ] Secure database credentials
- [ ] Test all customer/server combinations
- [ ] Enable HTTPS
- [ ] Add authentication
- [ ] Configure firewall rules
- [ ] Set up monitoring alerts
- [ ] Create backup strategy
- [ ] Document server access procedures
- [ ] Train users on dashboard usage
- [ ] Set up log rotation
- [ ] Configure auto-start on server reboot

---

## 🎉 Success!

Your production-ready GXO SQL Server Monitoring Dashboard is now configured with:
- ✅ Customer-based filtering
- ✅ Server-specific data display
- ✅ Real-time metrics
- ✅ Professional UI
- ✅ Robust error handling
- ✅ Production-ready API

**Access your dashboard at:** http://localhost:7070/monitoring

---

**Last Updated:** 2026-06-17  
**Version:** 2.0 (Production Ready)  
**Location:** C:\Users\00670T744\Videos\Python_SQLDBA