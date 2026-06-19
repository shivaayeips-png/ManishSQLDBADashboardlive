"""
SQL Server Metrics Collection Script
Collects availability, performance, and database metrics from SQL Server instances
"""

import pyodbc
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import time
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sql_monitoring.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SQLServerMonitor:
    """SQL Server monitoring and metrics collection"""
    
    def __init__(self, config_file: str = 'monitoring_config.json'):
        """Initialize monitor with configuration"""
        self.config = self._load_config(config_file)
        self.monitoring_conn_string = self._build_connection_string(
            self.config['monitoring_server']
        )
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), config_file)
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_file}")
            # Return default config
            return {
                "monitoring_server": {
                    "server": "localhost",
                    "database": "SQLServerMonitoring",
                    "use_windows_auth": True
                },
                "target_servers": ["localhost"]
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    def _build_connection_string(self, server_config: Dict) -> str:
        """Build SQL Server connection string"""
        if server_config.get('use_windows_auth', True):
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server_config['server']};"
                f"DATABASE={server_config.get('database', 'SQLServerMonitoring')};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server_config['server']};"
                f"DATABASE={server_config.get('database', 'SQLServerMonitoring')};"
                f"UID={server_config['username']};"
                f"PWD={server_config['password']};"
            )
    
    def test_server_availability(self, server: str) -> Dict[str, Any]:
        """Test SQL Server availability and response time"""
        start_time = time.time()
        
        try:
            conn_string = self._build_connection_string({'server': server, 'use_windows_auth': True})
            conn = pyodbc.connect(conn_string, timeout=5)
            cursor = conn.cursor()
            
            # Get version info
            cursor.execute("SELECT @@VERSION AS Version, SERVERPROPERTY('ProductVersion') AS ProductVersion")
            row = cursor.fetchone()
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            result = {
                'server_name': server,
                'is_available': True,
                'response_time_ms': round(response_time, 2),
                'version': row.Version if row else None,
                'product_version': row.ProductVersion if row else None,
                'error_message': None,
                'check_time': datetime.now().isoformat()
            }
            
            cursor.close()
            conn.close()
            
            logger.info(f"✓ Server {server} is ONLINE (Response: {result['response_time_ms']}ms)")
            return result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"✗ Server {server} is OFFLINE: {str(e)}")
            return {
                'server_name': server,
                'is_available': False,
                'response_time_ms': round(response_time, 2),
                'version': None,
                'product_version': None,
                'error_message': str(e),
                'check_time': datetime.now().isoformat()
            }
    
    def get_performance_metrics(self, server: str) -> Optional[Dict[str, Any]]:
        """Collect performance metrics from SQL Server"""
        try:
            conn_string = self._build_connection_string({'server': server, 'use_windows_auth': True})
            conn = pyodbc.connect(conn_string, timeout=30)
            cursor = conn.cursor()
            
            query = """
            SELECT 
                -- CPU Usage
                (SELECT TOP 1 
                    CAST(100 - record.value('(./Record/SchedulerMonitorEvent/SystemHealth/SystemIdle)[1]', 'int') AS DECIMAL(5,2))
                FROM (
                    SELECT CAST(record AS XML) AS record
                    FROM sys.dm_os_ring_buffers
                    WHERE ring_buffer_type = N'RING_BUFFER_SCHEDULER_MONITOR'
                    AND record LIKE '%<SystemHealth>%'
                ) AS x
                ORDER BY x.record.value('(./Record/@id)[1]', 'int') DESC
                ) AS CPUUsagePercent,
                
                -- Memory Usage
                (SELECT 
                    CAST((total_physical_memory_kb - available_physical_memory_kb) * 100.0 / total_physical_memory_kb AS DECIMAL(5,2))
                FROM sys.dm_os_sys_memory
                ) AS MemoryUsagePercent,
                
                -- Active Connections
                (SELECT COUNT(*) FROM sys.dm_exec_sessions WHERE is_user_process = 1) AS ActiveConnections,
                
                -- Total Connections
                (SELECT COUNT(*) FROM sys.dm_exec_sessions) AS TotalConnections,
                
                -- Blocked Sessions
                (SELECT COUNT(*) FROM sys.dm_exec_requests WHERE blocking_session_id > 0) AS BlockedSessions,
                
                -- Database Count (excluding system databases)
                (SELECT COUNT(*) FROM sys.databases WHERE state = 0 AND database_id > 4) AS OnlineDatabases,
                
                -- Total Database Size
                (SELECT CAST(SUM(size * 8.0 / 1024) AS DECIMAL(10,2)) FROM sys.master_files) AS TotalDatabaseSizeMB
            """
            
            cursor.execute(query)
            row = cursor.fetchone()
            
            if row:
                metrics = {
                    'server_name': server,
                    'cpu_usage_percent': float(row.CPUUsagePercent) if row.CPUUsagePercent else 0,
                    'memory_usage_percent': float(row.MemoryUsagePercent) if row.MemoryUsagePercent else 0,
                    'active_connections': row.ActiveConnections or 0,
                    'total_connections': row.TotalConnections or 0,
                    'blocked_sessions': row.BlockedSessions or 0,
                    'online_databases': row.OnlineDatabases or 0,
                    'total_database_size_mb': float(row.TotalDatabaseSizeMB) if row.TotalDatabaseSizeMB else 0,
                    'collection_time': datetime.now().isoformat()
                }
                
                logger.info(f"  CPU: {metrics['cpu_usage_percent']}% | Memory: {metrics['memory_usage_percent']}% | Connections: {metrics['active_connections']}")
                
                cursor.close()
                conn.close()
                return metrics
            
            cursor.close()
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics for {server}: {str(e)}")
            return None
    
    def get_database_availability(self, server: str) -> List[Dict[str, Any]]:
        """Get database availability information"""
        try:
            conn_string = self._build_connection_string({'server': server, 'use_windows_auth': True})
            conn = pyodbc.connect(conn_string, timeout=30)
            cursor = conn.cursor()
            
            query = """
            SELECT
                d.name AS DatabaseName,
                d.state_desc AS State,
                d.recovery_model_desc AS RecoveryModel,
                CAST(SUM(mf.size) * 8.0 / 1024 AS DECIMAL(10,2)) AS SizeMB,
                d.create_date AS CreateDate,
                d.compatibility_level AS CompatibilityLevel
            FROM sys.databases d
            LEFT JOIN sys.master_files mf ON d.database_id = mf.database_id
            WHERE d.database_id > 4
            GROUP BY d.name, d.state_desc, d.recovery_model_desc, d.create_date, d.compatibility_level
            ORDER BY d.name
            """
            
            cursor.execute(query)
            databases = []
            
            for row in cursor.fetchall():
                databases.append({
                    'server_name': server,
                    'database_name': row.DatabaseName,
                    'state': row.State,
                    'recovery_model': row.RecoveryModel,
                    'size_mb': float(row.SizeMB) if row.SizeMB else 0,
                    'create_date': row.CreateDate.isoformat() if row.CreateDate else None,
                    'compatibility_level': row.CompatibilityLevel,
                    'check_time': datetime.now().isoformat()
                })
            
            cursor.close()
            conn.close()
            
            logger.info(f"  Found {len(databases)} user databases")
            return databases
            
        except Exception as e:
            logger.error(f"Failed to get database availability for {server}: {str(e)}")
            return []
    def get_blocking_and_longrunning_queries(self, server: str, duration_threshold_seconds: int = 30) -> List[Dict[str, Any]]:
        """Get blocking queries and long-running sessions using sys.sysprocesses"""
        try:
            conn_string = self._build_connection_string({'server': server, 'use_windows_auth': True})
            conn = pyodbc.connect(conn_string, timeout=30)
            cursor = conn.cursor()
            
            # Query for all blocking-related sessions and long-running queries
            blocking_query = """
            -- Get head blockers (sessions blocking others but not blocked themselves)
            SELECT
                LEFT([sql].[text], 1000) as [text],
                CURRENT_TIMESTAMP as [time],
                p.spid,
                p.waittype,
                p.waittime,
                p.lastwaittype,
                p.waitresource,
                p.dbid,
                p.open_tran,
                p.status,
                p.cmd,
                DB_NAME(p.dbid) as database_name,
                p.blocked,
                p.hostname,
                p.program_name,
                p.loginame,
                'HEAD_BLOCKER' as query_type
            FROM sys.sysprocesses p
            OUTER APPLY sys.dm_exec_sql_text(p.sql_handle) sql
            WHERE p.spid IN (SELECT DISTINCT blocked FROM sys.sysprocesses WHERE blocked > 0)
                AND p.blocked = 0
                AND p.spid > 50  -- Exclude system processes
            
            UNION ALL
            
            -- Get blocked sessions
            SELECT
                LEFT([sql].[text], 1000) as [text],
                CURRENT_TIMESTAMP as [time],
                p.spid,
                p.waittype,
                p.waittime,
                p.lastwaittype,
                p.waitresource,
                p.dbid,
                p.open_tran,
                p.status,
                p.cmd,
                DB_NAME(p.dbid) as database_name,
                p.blocked,
                p.hostname,
                p.program_name,
                p.loginame,
                'BLOCKED' as query_type
            FROM sys.sysprocesses p
            OUTER APPLY sys.dm_exec_sql_text(p.sql_handle) sql
            WHERE p.blocked > 0
                AND p.spid > 50  -- Exclude system processes
            
            UNION ALL
            
            -- Get long-running queries (over threshold)
            SELECT
                LEFT([sql].[text], 1000) as [text],
                CURRENT_TIMESTAMP as [time],
                p.spid,
                p.waittype,
                p.waittime,
                p.lastwaittype,
                p.waitresource,
                p.dbid,
                p.open_tran,
                p.status,
                p.cmd,
                DB_NAME(p.dbid) as database_name,
                p.blocked,
                p.hostname,
                p.program_name,
                p.loginame,
                'LONG_RUNNING' as query_type
            FROM sys.sysprocesses p
            OUTER APPLY sys.dm_exec_sql_text(p.sql_handle) sql
            WHERE p.waittime > (? * 1000)  -- Convert seconds to milliseconds
                AND p.spid > 50  -- Exclude system processes
                AND p.blocked = 0  -- Not already counted as blocked
                AND p.spid NOT IN (SELECT DISTINCT blocked FROM sys.sysprocesses WHERE blocked > 0)  -- Not already counted as head blocker
            """
            
            cursor.execute(blocking_query, (duration_threshold_seconds,))
            queries = []
            
            for row in cursor.fetchall():
                # Count how many sessions this is blocking (only for head blockers)
                blocking_count = 0
                if row.query_type == 'HEAD_BLOCKER':
                    cursor_check = conn.cursor()
                    cursor_check.execute(
                        "SELECT COUNT(*) FROM sys.sysprocesses WHERE blocked = ?",
                        (row.spid,)
                    )
                    result = cursor_check.fetchone()
                    blocking_count = result[0] if result else 0
                    cursor_check.close()
                
                queries.append({
                    'server_name': server,
                    'session_id': row.spid,
                    'login_name': row.loginame or 'N/A',
                    'database_name': row.database_name or 'N/A',
                    'status': row.status or 'N/A',
                    'command': row.cmd or 'N/A',
                    'blocking_session_id': row.blocked or 0,
                    'wait_type': str(row.waittype) if row.waittype else 'N/A',
                    'wait_time_ms': row.waittime or 0,
                    'last_wait_type': row.lastwaittype or 'N/A',
                    'wait_resource': row.waitresource or 'N/A',
                    'open_transactions': row.open_tran or 0,
                    'elapsed_time_seconds': (row.waittime or 0) / 1000,  # Convert ms to seconds
                    'query_text': (row.text or 'N/A').strip(),
                    'host_name': row.hostname or 'N/A',
                    'program_name': row.program_name or 'N/A',
                    'start_time': row.time.isoformat() if row.time else None,
                    'query_type': row.query_type,
                    'blocking_count': blocking_count,
                    'check_time': datetime.now().isoformat()
                })
            
            cursor.close()
            conn.close()
            
            if queries:
                logger.info(f"  Found {len(queries)} head blocker queries")
            return queries
            
        except Exception as e:
            logger.error(f"Failed to get blocking/long-running queries for {server}: {str(e)}")
            return []
    
    
    def save_server_metrics(self, availability: Dict, performance: Optional[Dict]):
        """Save server metrics to monitoring database"""
        try:
            conn = pyodbc.connect(self.monitoring_conn_string)
            cursor = conn.cursor()
            
            # Insert server availability
            cursor.execute("""
                INSERT INTO ServerAvailability (
                    ServerName, IsAvailable, ResponseTimeMs, Version, ProductVersion,
                    ErrorMessage, CheckTime
                )
                VALUES (?, ?, ?, ?, ?, ?, GETDATE())
            """, (
                availability['server_name'],
                availability['is_available'],
                availability['response_time_ms'],
                availability['version'],
                availability['product_version'],
                availability['error_message']
            ))
            
            # Insert performance metrics if available
            if performance:
                cursor.execute("""
                    INSERT INTO PerformanceMetrics (
                        ServerName, CPUUsagePercent, MemoryUsagePercent, 
                        ActiveConnections, TotalConnections, BlockedSessions,
                        OnlineDatabases, TotalDatabaseSizeMB, CollectionTime
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
                """, (
                    performance['server_name'],
                    performance['cpu_usage_percent'],
                    performance['memory_usage_percent'],
                    performance['active_connections'],
                    performance['total_connections'],
                    performance['blocked_sessions'],
                    performance['online_databases'],
                    performance['total_database_size_mb']
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✓ Saved metrics for server: {availability['server_name']}")
            
        except Exception as e:
            logger.error(f"Failed to save metrics for {availability['server_name']}: {str(e)}")
    
    def save_database_metrics(self, databases: List[Dict]):
        """Save database metrics to monitoring database"""
        try:
            conn = pyodbc.connect(self.monitoring_conn_string)
            cursor = conn.cursor()
            
            for db in databases:
                cursor.execute("""
                    INSERT INTO DatabaseAvailability (
                        ServerName, DatabaseName, State, RecoveryModel,
                        SizeMB, CreateDate, CompatibilityLevel, CheckTime
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())
                """, (
                    db['server_name'],
                    db['database_name'],
                    db['state'],
                    db['recovery_model'],
                    db['size_mb'],
                    db['create_date'],
                    db['compatibility_level']
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            if databases:
                logger.info(f"✓ Saved database metrics for server: {databases[0]['server_name']} ({len(databases)} databases)")
            
        except Exception as e:
            logger.error(f"Failed to save database metrics: {str(e)}")
    
    def collect_all_metrics(self):
        """Collect metrics from all configured servers"""
        logger.info("\n=== SQL Server Monitoring Data Collection ===")
        logger.info(f"Monitoring Database: {self.config['monitoring_server']['database']} on {self.config['monitoring_server']['server']}\n")
        
        for server in self.config['target_servers']:
            logger.info(f"Collecting metrics for: {server}")
            
            # Check server availability
            availability = self.test_server_availability(server)
            
            if availability['is_available']:
                # Get performance metrics
                performance = self.get_performance_metrics(server)
                
                # Get database availability
                databases = self.get_database_availability(server)
                
                # Save all metrics
                self.save_server_metrics(availability, performance)
                self.save_database_metrics(databases)
            else:
                # Save only availability data for offline servers
                self.save_server_metrics(availability, None)
            
            logger.info("")
        
        logger.info("=== Collection Complete ===\n")


def main():
    """Main execution function"""
    try:
        monitor = SQLServerMonitor('monitoring_config.json')
        monitor.collect_all_metrics()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob