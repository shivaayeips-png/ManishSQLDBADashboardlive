"""
Execute SQL fix script to create/update sp_GetDashboardSummary stored procedure
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

# Read SQL script
with open('sql/Fix-DatabaseCount.sql', 'r') as f:
    sql_script = f.read()

# Split by GO statements
sql_batches = [batch.strip() for batch in sql_script.split('GO') if batch.strip() and not batch.strip().startswith('--')]

# Execute each batch
try:
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()
    
    for i, batch in enumerate(sql_batches):
        if batch and not batch.startswith('PRINT'):
            try:
                cursor.execute(batch)
                conn.commit()
                print(f"[OK] Executed batch {i+1}/{len(sql_batches)}")
            except Exception as e:
                print(f"[ERROR] Error in batch {i+1}: {e}")
    
    cursor.close()
    conn.close()
    
    print("\n[SUCCESS] SQL fix script executed successfully!")
    print("[SUCCESS] Stored procedure sp_GetDashboardSummary created/updated")
    print("\nPlease refresh your dashboard (Ctrl+F5) to see the corrected database count.")
    
except Exception as e:
    print(f"[FAILED] Failed to execute SQL script: {e}")

# Made with Bob
