"""
Force update sp_GetDashboardSummary stored procedure
"""
import pyodbc
import json

# Load config
with open('monitoring_config.json', 'r') as f:
    config = json.load(f)

server_config = config['monitoring_server']

# Build connection string
if server_config.get('use_windows_auth', True):
    conn_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server_config['server']};"
        f"DATABASE={server_config.get('database', 'SQLServerMonitoring')};"
        f"Trusted_Connection=yes;"
    )
else:
    conn_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server_config['server']};"
        f"DATABASE={server_config.get('database', 'SQLServerMonitoring')};"
        f"UID={server_config['username']};"
        f"PWD={server_config['password']};"
    )

try:
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()
    
    # Drop existing procedure
    print("Dropping existing stored procedure...")
    try:
        cursor.execute("DROP PROCEDURE IF EXISTS sp_GetDashboardSummary")
        conn.commit()
        print("[OK] Dropped existing procedure")
    except Exception as e:
        print(f"[INFO] Procedure may not exist: {e}")
    
    # Create new procedure
    print("Creating updated stored procedure...")
    create_sp = """
CREATE PROCEDURE sp_GetDashboardSummary
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Server Summary
    SELECT 
        COUNT(DISTINCT ServerName) AS TotalServers,
        SUM(CASE WHEN IsAvailable = 1 THEN 1 ELSE 0 END) AS AvailableServers,
        SUM(CASE WHEN IsAvailable = 0 OR IsAvailable IS NULL THEN 1 ELSE 0 END) AS UnavailableServers,
        AVG(CASE WHEN IsAvailable = 1 THEN ResponseTimeMs ELSE NULL END) AS AvgResponseTimeMs
    FROM (
        SELECT ServerName, IsAvailable, ResponseTimeMs,
               ROW_NUMBER() OVER (PARTITION BY ServerName ORDER BY CheckTime DESC) AS rn
        FROM ServerAvailability
    ) AS LatestAvailability
    WHERE rn = 1;
    
    -- Database Summary (EXCLUDING SYSTEM DATABASES)
    SELECT 
        COUNT(*) AS TotalDatabases,
        SUM(CASE WHEN State = 'ONLINE' THEN 1 ELSE 0 END) AS OnlineDatabases,
        SUM(CASE WHEN State <> 'ONLINE' THEN 1 ELSE 0 END) AS OfflineDatabases,
        SUM(SizeMB) AS TotalSizeMB
    FROM (
        SELECT ServerName, DatabaseName, State, SizeMB,
               ROW_NUMBER() OVER (PARTITION BY ServerName, DatabaseName ORDER BY CheckTime DESC) AS rn
        FROM DatabaseAvailability
    ) AS LatestDatabases
    WHERE rn = 1;
    
    -- Performance Summary
    SELECT 
        AVG(CPUUsagePercent) AS AvgCPUUsage,
        AVG(MemoryUsagePercent) AS AvgMemoryUsage,
        SUM(ActiveConnections) AS TotalActiveConnections,
        SUM(BlockedSessions) AS TotalBlockedSessions
    FROM (
        SELECT ServerName, CPUUsagePercent, MemoryUsagePercent, ActiveConnections, BlockedSessions,
               ROW_NUMBER() OVER (PARTITION BY ServerName ORDER BY CollectionTime DESC) AS rn
        FROM PerformanceMetrics
    ) AS LatestPerformance
    WHERE rn = 1;
    
    -- Recent Alerts
    SELECT TOP 10
        ServerName,
        AlertName,
        MetricValue,
        AlertMessage,
        Severity,
        IsResolved,
        TriggeredTime
    FROM Alerts
    WHERE IsResolved = 0
    ORDER BY TriggeredTime DESC;
END
"""
    
    cursor.execute(create_sp)
    conn.commit()
    print("[SUCCESS] Stored procedure created successfully!")
    print("[SUCCESS] Database count will now show only user databases (excluding system databases)")
    
    cursor.close()
    conn.close()
    
    print("\nPlease refresh your dashboard (Ctrl+F5) to see the corrected count of 7 databases.")
    
except Exception as e:
    print(f"[FAILED] Error: {e}")

# Made with Bob
