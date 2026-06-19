import pyodbc
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to database
conn_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=00670T\\MANISHPREET;"
    "DATABASE=SQLServerMonitoring;"
    "UID=manish;"
    "PWD=manish@79;"
)

try:
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()
    
    # Delete old servers
    servers_to_delete = ['localhost\\MANISHPREET', 'preet']
    
    for server in servers_to_delete:
        logger.info(f"Deleting data for server: {server}")
        
        # Delete from ServerAvailability
        cursor.execute("DELETE FROM ServerAvailability WHERE ServerName = ?", server)
        rows1 = cursor.rowcount
        
        # Delete from PerformanceMetrics
        cursor.execute("DELETE FROM PerformanceMetrics WHERE ServerName = ?", server)
        rows2 = cursor.rowcount
        
        # Delete from DatabaseAvailability
        cursor.execute("DELETE FROM DatabaseAvailability WHERE ServerName = ?", server)
        rows3 = cursor.rowcount
        
        logger.info(f"  Deleted {rows1} rows from ServerAvailability")
        logger.info(f"  Deleted {rows2} rows from PerformanceMetrics")
        logger.info(f"  Deleted {rows3} rows from DatabaseAvailability")
    
    conn.commit()
    logger.info("✓ Successfully cleaned old server data")
    
    # Verify remaining servers
    cursor.execute("SELECT DISTINCT ServerName FROM ServerAvailability")
    remaining = [row.ServerName for row in cursor.fetchall()]
    logger.info(f"Remaining servers in database: {remaining}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    logger.error(f"Error cleaning database: {e}")

# Made with Bob
