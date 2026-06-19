"""
Flask API for SQL Server Monitoring Dashboard
Provides REST endpoints for dashboard data with customer filtering
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import pyodbc
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from collect_sql_metrics import SQLServerMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


class DashboardAPI:
    """Dashboard API data provider"""
    
    def __init__(self, config_file: str = 'monitoring_config.json',
                 customer_config_file: str = 'customer_config.json'):
        """Initialize API with configuration"""
        self.config = self._load_config(config_file)
        self.customers = self._load_customer_config(customer_config_file)
        self.conn_string = self._build_connection_string(
            self.config['monitoring_server']
        )
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), config_file)
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {
                "monitoring_server": {
                    "server": "00670T\\MANISHPREET",
                    "database": "SQLServerMonitoring",
                    "use_windows_auth": False,
                    "username": "manish",
                    "password": "manish@79"
                }
            }
    
    def _load_customer_config(self, customer_config_file: str) -> List[Dict]:
        """Load customer configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), customer_config_file)
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('customers', [])
        except FileNotFoundError:
            logger.warning(f"Customer config file not found: {customer_config_file}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in customer config file: {e}")
            return []
    
    def _build_connection_string(self, server_config: Dict) -> str:
        """Build SQL Server connection string"""
        server_name = server_config['server']
        port = server_config.get('port')
        database_name = server_config.get('database', 'SQLServerMonitoring')

        server_target = server_name
        if port:
            host_name = server_name.split('\\')[0]
            server_target = f"{host_name},{port}"

        if server_config.get('use_windows_auth', True):
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server_target};"
                f"DATABASE={database_name};"
                f"Trusted_Connection=yes;"
                f"Connection Timeout=5;"
            )
        else:
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server_target};"
                f"DATABASE={database_name};"
                f"UID={server_config['username']};"
                f"PWD={server_config['password']};"
                f"Connection Timeout=5;"
            )
    
    def get_customers(self, limit: Optional[int] = None) -> List[Dict]:
        """Get list of customers with server details"""
        customers = self.customers if limit is None or limit <= 0 else self.customers[:limit]
        return [{
            'customer_id': c['customer_id'],
            'customer_name': c['customer_name'],
            'priority': c.get('priority'),
            'server_count': len(c.get('servers', [])),
            'contact_email': c.get('contact_email'),
            'servers': c.get('servers', [])
        } for c in customers]
    
    def get_customer_servers(self, customer_id: int) -> Optional[Dict]:
        """Get servers for a specific customer"""
        for customer in self.customers:
            if customer['customer_id'] == customer_id:
                return {
                    'customer_id': customer['customer_id'],
                    'customer_name': customer['customer_name'],
                    'priority': customer['priority'],
                    'servers': customer['servers'],
                    'contact_email': customer['contact_email']
                }
        return None
    
    def get_dashboard_summary(self) -> Dict:
        """Get dashboard summary data"""
        try:
            conn = pyodbc.connect(self.conn_string)
            cursor = conn.cursor()
            
            # Execute stored procedure
            cursor.execute("EXEC sp_GetDashboardSummary")
            
            # Get server summary
            server_summary = {}
            if cursor.description:
                row = cursor.fetchone()
                if row:
                    server_summary = {
                        'TotalServers': row.TotalServers,
                        'AvailableServers': row.AvailableServers,
                        'UnavailableServers': row.UnavailableServers,
                        'AvgResponseTimeMs': float(row.AvgResponseTimeMs) if row.AvgResponseTimeMs else 0
                    }
            
            # Get database summary
            cursor.nextset()
            database_summary = {}
            if cursor.description:
                row = cursor.fetchone()
                if row:
                    database_summary = {
                        'TotalDatabases': row.TotalDatabases,
                        'OnlineDatabases': row.OnlineDatabases,
                        'OfflineDatabases': row.OfflineDatabases,
                        'TotalSizeMB': float(row.TotalSizeMB) if row.TotalSizeMB else 0
                    }
            
            # Get performance summary
            cursor.nextset()
            performance_summary = {}
            if cursor.description:
                row = cursor.fetchone()
                if row:
                    performance_summary = {
                        'AvgCPUUsage': float(row.AvgCPUUsage) if row.AvgCPUUsage else 0,
                        'AvgMemoryUsage': float(row.AvgMemoryUsage) if row.AvgMemoryUsage else 0,
                        'TotalActiveConnections': row.TotalActiveConnections or 0,
                        'TotalBlockedSessions': row.TotalBlockedSessions or 0
                    }
            
            # Get recent alerts
            cursor.nextset()
            recent_alerts = []
            if cursor.description:
                for row in cursor.fetchall():
                    recent_alerts.append({
                        'ServerName': row.ServerName,
                        'AlertName': row.AlertName,
                        'MetricValue': float(row.MetricValue) if row.MetricValue else 0,
                        'AlertMessage': row.AlertMessage,
                        'Severity': row.Severity,
                        'IsResolved': row.IsResolved,
                        'TriggeredTime': row.TriggeredTime.isoformat() if row.TriggeredTime else None
                    })
            
            cursor.close()
            conn.close()
            
            return {
                'serverSummary': server_summary,
                'databaseSummary': database_summary,
                'performanceSummary': performance_summary,
                'recentAlerts': recent_alerts,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard summary: {e}")
            raise
    
    def get_server_status(self, server_name: Optional[str] = None) -> List[Dict]:
        """Get current server status"""
        try:
            conn = pyodbc.connect(self.conn_string)
            cursor = conn.cursor()
            
            if server_name:
                query = "SELECT * FROM vw_CurrentServerStatus WHERE ServerName = ? ORDER BY ServerName"
                cursor.execute(query, server_name)
            else:
                query = "SELECT * FROM vw_CurrentServerStatus ORDER BY ServerName"
                cursor.execute(query)
            
            servers = []
            for row in cursor.fetchall():
                servers.append({
                    'ServerName': row.ServerName,
                    'IsAvailable': row.IsAvailable,
                    'ResponseTimeMs': float(row.ResponseTimeMs) if row.ResponseTimeMs else 0,
                    'Version': row.Version,
                    'CPUUsagePercent': float(row.CPUUsagePercent) if row.CPUUsagePercent else 0,
                    'MemoryUsagePercent': float(row.MemoryUsagePercent) if row.MemoryUsagePercent else 0,
                    'ActiveConnections': row.ActiveConnections or 0,
                    'TotalConnections': row.TotalConnections or 0,
                    'BlockedSessions': row.BlockedSessions or 0,
                    'OnlineDatabaseCount': row.OnlineDatabaseCount or 0,
                    'OfflineDatabaseCount': row.OfflineDatabaseCount or 0,
                    'CheckTime': row.CheckTime.isoformat() if row.CheckTime else None
                })
            
            cursor.close()
            conn.close()
            
            return servers
            
        except Exception as e:
            logger.error(f"Failed to get server status: {e}")
            raise
    
    def get_database_status(self, server_name: Optional[str] = None) -> List[Dict]:
        """Get database status"""
        try:
            conn = pyodbc.connect(self.conn_string)
            cursor = conn.cursor()
            
            if server_name:
                query = "SELECT * FROM vw_DatabaseStatusSummary WHERE ServerName = ? ORDER BY ServerName, DatabaseName"
                cursor.execute(query, server_name)
            else:
                query = "SELECT * FROM vw_DatabaseStatusSummary ORDER BY ServerName, DatabaseName"
                cursor.execute(query)
            
            databases = []
            for row in cursor.fetchall():
                databases.append({
                    'ServerName': row.ServerName,
                    'DatabaseName': row.DatabaseName,
                    'State': row.State,
                    'RecoveryModel': row.RecoveryModel,
                    'SizeMB': float(row.SizeMB) if row.SizeMB else 0,
                    'CreateDate': row.CreateDate.isoformat() if row.CreateDate else None,
                    'CompatibilityLevel': row.CompatibilityLevel,
                    'CheckTime': row.CheckTime.isoformat() if row.CheckTime else None
                })
            
            cursor.close()
            conn.close()
            
            return databases
            
        except Exception as e:
            logger.error(f"Failed to get database status: {e}")
            raise
    
    def get_performance_history(self, server_name: str, hours: int = 24) -> Dict:
        """Get performance history for a server"""
        try:
            conn = pyodbc.connect(self.conn_string)
            cursor = conn.cursor()
            
            cursor.execute("EXEC sp_GetServerHistory @ServerName=?, @Hours=?", server_name, hours)
            
            # Get availability history
            availability_history = []
            if cursor.description:
                for row in cursor.fetchall():
                    availability_history.append({
                        'CheckTime': row.CheckTime.isoformat() if row.CheckTime else None,
                        'IsAvailable': row.IsAvailable,
                        'ResponseTimeMs': float(row.ResponseTimeMs) if row.ResponseTimeMs else 0
                    })
            
            # Get performance history
            cursor.nextset()
            performance_history = []
            if cursor.description:
                for row in cursor.fetchall():
                    performance_history.append({
                        'CollectionTime': row.CollectionTime.isoformat() if row.CollectionTime else None,
                        'CPUUsagePercent': float(row.CPUUsagePercent) if row.CPUUsagePercent else 0,
                        'MemoryUsagePercent': float(row.MemoryUsagePercent) if row.MemoryUsagePercent else 0,
                        'ActiveConnections': row.ActiveConnections or 0,
                        'BlockedSessions': row.BlockedSessions or 0
                    })
            
            cursor.close()
            conn.close()
            
            return {
                'serverName': server_name,
                'availabilityHistory': availability_history,
                'performanceHistory': performance_history
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance history: {e}")
            raise
    
    def get_blocking_and_longrunning_queries(self, server_name: str, duration_threshold: int = 30) -> List[Dict]:
        """Get blocking and long-running queries for a server"""
        try:
            monitor = SQLServerMonitor()
            queries = monitor.get_blocking_and_longrunning_queries(server_name, duration_threshold)
            return queries
        except Exception as e:
            logger.error(f"Failed to get blocking/long-running queries for {server_name}: {e}")
            return []


# Initialize API
api = DashboardAPI()


# Load dashboard HTML template
def load_dashboard_html():
    """Load the dashboard HTML file with cache busting"""
    import time
    try:
        # Use blocking dashboard (with blocking queries feature)
        with open('customer_dashboard_blocking.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            # Add cache-busting version parameter
            version = str(int(time.time()))
            html_content = html_content.replace('</head>', f'<meta name="version" content="{version}"></head>')
            return html_content
    except FileNotFoundError:
        # Fallback to v2
        try:
            with open('customer_dashboard_v2.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
                version = str(int(time.time()))
                html_content = html_content.replace('</head>', f'<meta name="version" content="{version}"></head>')
                return html_content
        except FileNotFoundError:
            return "<h1>Dashboard HTML file not found</h1>"

# Dashboard Route
@app.route('/monitoring', methods=['GET'])
def monitoring_dashboard():
    """Serve the monitoring dashboard with no-cache headers"""
    html_content = load_dashboard_html()
    response = app.make_response(html_content)
    # Prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/monitoring/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard summary"""
    try:
        data = api.get_dashboard_summary()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/servers', methods=['GET'])
def get_servers():
    """Get server status"""
    try:
        server_name = request.args.get('server')
        data = api.get_server_status(server_name)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/databases', methods=['GET'])
def get_databases():
    """Get database status"""
    try:
        server_name = request.args.get('server')
        data = api.get_database_status(server_name)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/performance/<server_name>', methods=['GET'])
def get_performance(server_name):
    """Get performance history for a server"""
    try:
        hours = int(request.args.get('hours', 24))
        data = api.get_performance_history(server_name, hours)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/config', methods=['GET'])
def get_config():
    """Get monitoring configuration"""
    try:
        return jsonify({
            'target_servers': api.config.get('target_servers', []),
            'collection_interval': api.config.get('collection_interval_seconds', 30),
            'alert_thresholds': api.config.get('alert_thresholds', {})
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/customers', methods=['GET'])
def get_customers():
    """Get list of customers (Top 10)"""
    try:
        limit = int(request.args.get('limit', 0))
        customers = api.get_customers(limit)
        return jsonify({
            'customers': customers,
            'total': len(customers)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/customers/<int:customer_id>', methods=['GET'])
def get_customer_details(customer_id):
    """Get customer details with servers"""
    try:
        customer = api.get_customer_servers(customer_id)
        if customer:
            return jsonify(customer)
        else:
            return jsonify({'error': f'Customer {customer_id} not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/customers/<int:customer_id>/status', methods=['GET'])
def get_customer_status(customer_id):
    """Get real-time status for a customer's servers and databases"""
    try:
        customer = api.get_customer_servers(customer_id)
        if not customer:
            return jsonify({'error': f'Customer {customer_id} not found'}), 404
        
        # Get server instances for this customer
        server_instances = [s['server_instance'] for s in customer['servers']]
        
        # Get status for these servers
        servers_status = []
        databases_status = []
        
        for server_instance in server_instances:
            server_data = api.get_server_status(server_instance)
            if server_data:
                servers_status.extend(server_data)
            
            db_data = api.get_database_status(server_instance)
            if db_data:
                databases_status.extend(db_data)
        
        return jsonify({
            'customer_id': customer['customer_id'],
            'customer_name': customer['customer_name'],
            'priority': customer['priority'],
            'servers': servers_status,
            'databases': databases_status,
            'summary': {
                'total_servers': len(customer['servers']),
                'available_servers': sum(1 for s in servers_status if s.get('IsAvailable')),
                'total_databases': len(databases_status),
                'online_databases': sum(1 for d in databases_status if d.get('State') == 'ONLINE')
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/server-details', methods=['GET'])
def get_server_details():
    """Get detailed server and database information for a specific server"""
    try:
        server_name = request.args.get('server')
        if not server_name:
            return jsonify({'error': 'server parameter is required'}), 400
        
        # Get server status
        server_data = api.get_server_status(server_name)
        server_status = server_data[0] if server_data and len(server_data) > 0 else None
        
        # Get databases for this server
        databases = api.get_database_status(server_name)
        
        # Calculate metrics
        total_databases = len(databases)
        online_databases = sum(1 for db in databases if db.get('State') == 'ONLINE')
        offline_databases = total_databases - online_databases
        total_size_mb = sum(db.get('SizeMB', 0) for db in databases)
        
        # Server metrics
        is_available = server_status.get('IsAvailable', False) if server_status else False
        cpu_usage = server_status.get('CPUUsagePercent', 0) if server_status else 0
        memory_usage = server_status.get('MemoryUsagePercent', 0) if server_status else 0
        active_connections = server_status.get('ActiveConnections', 0) if server_status else 0
        blocked_sessions = server_status.get('BlockedSessions', 0) if server_status else 0
        response_time = server_status.get('ResponseTimeMs', 0) if server_status else 0
        
        return jsonify({
            'server_name': server_name,
            'server_status': {
                'is_available': is_available,
                'response_time_ms': response_time,
                'cpu_usage_percent': cpu_usage,
                'memory_usage_percent': memory_usage,
                'active_connections': active_connections,
                'blocked_sessions': blocked_sessions,
                'version': server_status.get('Version', 'Unknown') if server_status else 'Unknown'
            },
            'database_summary': {
                'total_databases': total_databases,
                'online_databases': online_databases,
                'offline_databases': offline_databases,
                'total_size_mb': total_size_mb
            },
            'databases': databases,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting server details: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/blocking-queries', methods=['GET'])
def get_blocking_queries():
    """Get blocking and long-running queries for a server"""
    try:
        server_name = request.args.get('server')
        if not server_name:
            return jsonify({'error': 'server parameter is required'}), 400
        
        duration_threshold = int(request.args.get('threshold', 30))
        queries = api.get_blocking_and_longrunning_queries(server_name, duration_threshold)
        
        return jsonify({
            'server_name': server_name,
            'duration_threshold_seconds': duration_threshold,
            'query_count': len(queries),
            'queries': queries,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting blocking queries: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("Starting SQL Server Monitoring Dashboard API...")
    logger.info("Dashboard will be available at http://localhost:7070/monitoring")
    logger.info("API will be available at http://localhost:7070")
    logger.info("\nDashboard Endpoints:")
    logger.info("  GET /monitoring - SQL Server Monitoring Dashboard")
    logger.info("\nAPI Endpoints:")
    logger.info("  GET /api/monitoring/dashboard - Dashboard summary data")
    logger.info("  GET /api/monitoring/servers - Server status")
    logger.info("  GET /api/monitoring/databases - Database status")
    logger.info("  GET /api/monitoring/customers - List all customers")
    logger.info("  GET /api/monitoring/customers/<id> - Get customer details")
    logger.info("  GET /api/monitoring/customers/<id>/status - Get customer server/DB status")
    app.run(host='0.0.0.0', port=7070, debug=True)

# Made with Bob