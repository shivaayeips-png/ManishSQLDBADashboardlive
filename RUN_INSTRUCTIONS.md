# 🚀 HOW TO RUN THE CUSTOMER MONITORING DASHBOARD

## 📍 File Locations

All files are located in:
```
C:\Users\00670T744\Videos\Python_SQLDBA\
```

## ⚡ QUICK START - 3 METHODS

### METHOD 1: One-Click Startup (EASIEST) ⭐

**Step 1:** Open File Explorer and navigate to:
```
C:\Users\00670T744\Videos\Python_SQLDBA
```

**Step 2:** Double-click this file:
```
START_CUSTOMER_DASHBOARD.bat
```

**Step 3:** The dashboard will automatically open in your browser!

---

### METHOD 2: Manual Startup

**Step 1:** Open Command Prompt (cmd) or PowerShell

**Step 2:** Navigate to the project folder:
```cmd
cd C:\Users\00670T744\Videos\Python_SQLDBA
```

**Step 3:** Setup database (first time only):
```cmd
sqlcmd -S 00670T744\MANISHPREET -U manish -P manish@79 -d SQLServerMonitoring -i sql\Create-CustomerTables.sql
```

**Step 4:** Start the API server:
```cmd
python dashboard_api.py
```

**Step 5:** Open the dashboard in your browser:
- Open File Explorer
- Navigate to: `C:\Users\00670T744\Videos\Python_SQLDBA`
- Double-click: `customer_dashboard.html`

**OR** paste this in your browser address bar:
```
file:///C:/Users/00670T744/Videos/Python_SQLDBA/customer_dashboard.html
```

---

### METHOD 3: Python Monitoring Script (Command Line)

**Step 1:** Open Command Prompt

**Step 2:** Navigate to folder:
```cmd
cd C:\Users\00670T744\Videos\Python_SQLDBA
```

**Step 3:** Run the monitoring script:
```cmd
python customer_monitoring.py
```

**Step 4:** Select customer:
- Enter **1-10** for specific customer
- Enter **all** to monitor all customers
- Enter **exit** to quit

---

## 🌐 Access URLs

Once running, you can access:

### Dashboard (Web Interface):
```
file:///C:/Users/00670T744/Videos/Python_SQLDBA/customer_dashboard.html
```

### API Endpoints:
```
http://localhost:5000/api/monitoring/customers
http://localhost:5000/api/monitoring/customers/1
http://localhost:5000/api/monitoring/customers/1/status
```

---

## 📂 Direct File Paths

### Main Files:

**Startup Script:**
```
C:\Users\00670T744\Videos\Python_SQLDBA\START_CUSTOMER_DASHBOARD.bat
```

**Dashboard HTML:**
```
C:\Users\00670T744\Videos\Python_SQLDBA\customer_dashboard.html
```

**Python Monitoring Script:**
```
C:\Users\00670T744\Videos\Python_SQLDBA\customer_monitoring.py
```

**API Server:**
```
C:\Users\00670T744\Videos\Python_SQLDBA\dashboard_api.py
```

**Database Setup:**
```
C:\Users\00670T744\Videos\Python_SQLDBA\sql\Create-CustomerTables.sql
```

**Configuration:**
```
C:\Users\00670T744\Videos\Python_SQLDBA\customer_config.json
```

**Documentation:**
```
C:\Users\00670T744\Videos\Python_SQLDBA\CUSTOMER_MONITORING_GUIDE.md
```

---

## 🎯 Step-by-Step Visual Guide

### Using Windows Explorer:

1. **Press** `Windows Key + E` to open File Explorer

2. **Copy and paste** this path in the address bar:
   ```
   C:\Users\00670T744\Videos\Python_SQLDBA
   ```

3. **Press Enter**

4. You will see these files:
   - ✅ `START_CUSTOMER_DASHBOARD.bat` ← **DOUBLE-CLICK THIS**
   - `customer_dashboard.html`
   - `customer_monitoring.py`
   - `dashboard_api.py`
   - `customer_config.json`

5. **Double-click** `START_CUSTOMER_DASHBOARD.bat`

6. Wait 5-10 seconds, dashboard will open automatically!

---

## 🔧 Troubleshooting

### If Dashboard Doesn't Open:

**Option A:** Manually open the HTML file:
1. Navigate to: `C:\Users\00670T744\Videos\Python_SQLDBA`
2. Right-click `customer_dashboard.html`
3. Select "Open with" → Choose your browser (Chrome, Edge, Firefox)

**Option B:** Use browser directly:
1. Open your web browser
2. Press `Ctrl + O` (Open File)
3. Navigate to: `C:\Users\00670T744\Videos\Python_SQLDBA`
4. Select `customer_dashboard.html`
5. Click Open

### If API Server Doesn't Start:

Check if Python is installed:
```cmd
python --version
```

If not installed, download from: https://www.python.org/downloads/

Install dependencies:
```cmd
cd C:\Users\00670T744\Videos\Python_SQLDBA
pip install -r requirements.txt
```

---

## 📱 Quick Access Shortcuts

### Create Desktop Shortcut:

1. Navigate to: `C:\Users\00670T744\Videos\Python_SQLDBA`
2. Right-click `START_CUSTOMER_DASHBOARD.bat`
3. Select "Send to" → "Desktop (create shortcut)"
4. Now you can run it from your desktop!

### Pin to Taskbar:

1. Right-click `START_CUSTOMER_DASHBOARD.bat`
2. Select "Pin to taskbar"

---

## 🎬 What Happens When You Run It?

1. ✅ Database tables are created (if not exists)
2. ✅ API server starts on http://localhost:5000
3. ✅ Dashboard opens in your default browser
4. ✅ You can select customers from dropdown
5. ✅ Real-time monitoring data is displayed

---

## 📊 Using the Dashboard

Once the dashboard opens:

1. **Select Customer** from the dropdown menu (Top 10 customers)
2. **View Status** - Automatically loads:
   - Server availability (Online/Offline)
   - Database availability (Online/Offline)
   - Performance metrics (CPU, Memory, Connections)
3. **Refresh** - Click the refresh button for latest data

---

## 💡 Pro Tips

### Keep API Running:
The API server window must stay open for the dashboard to work. Don't close it!

### Multiple Customers:
You can monitor multiple customers by selecting different ones from the dropdown.

### Command Line Monitoring:
For automated monitoring, use:
```cmd
python customer_monitoring.py
```

### View Logs:
Check these files for troubleshooting:
- `customer_monitoring.log`
- `sql_monitoring.log`

---

## 🆘 Need Help?

1. **Check logs** in the project folder
2. **Verify SQL Server** is running
3. **Test connection** to: `00670T744\MANISHPREET`
4. **Review documentation**: `CUSTOMER_MONITORING_GUIDE.md`

---

## ✅ Success Checklist

- [ ] Navigated to `C:\Users\00670T744\Videos\Python_SQLDBA`
- [ ] Double-clicked `START_CUSTOMER_DASHBOARD.bat`
- [ ] API server window opened
- [ ] Dashboard opened in browser
- [ ] Can see customer dropdown
- [ ] Can select and view customer data

---

## 🎉 You're All Set!

**Main Path:** `C:\Users\00670T744\Videos\Python_SQLDBA`

**Main File:** `START_CUSTOMER_DASHBOARD.bat`

**Just double-click and go!** 🚀

---

**Last Updated:** 2026-06-15  
**Location:** C:\Users\00670T744\Videos\Python_SQLDBA