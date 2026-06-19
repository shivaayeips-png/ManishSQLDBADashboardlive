"""
SQL Server Alert System
Monitors metrics and sends alerts when thresholds are exceeded
"""

import pyodbc
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlertSystem:
    """SQL Server monitoring alert system"""
    
    def __init__(self, config_file: str = 'monitoring_config.json'):
        """Initialize alert system with configuration"""
        self.config = self._load_config(config_file)
        self.monitoring_conn_string = self._build_connection_string(
            self.config['monitoring_server']
        )
        self.thresholds = self.config.get('alert_thresholds', {})
        self.email_config = self.config.get('email_alerts', {})
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), config_file)
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
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
    
    def check_server_availability_alerts(self) -> List[Dict]:
        """Check for server availability issues"""
        alerts = []
        
        try:
            conn = pyodbc.connect(self.monitoring_conn_string)
            cursor = conn.cursor()
            
            # Check for servers that are down
            query = """
            SELECT 
                ServerName,
                IsAvailable,
                ResponseTimeMs,
                ErrorMessage,
                CheckTime
            FROM ServerAvailability
            WHERE CheckTime >= DATEADD(MINUTE, -5, GETDATE())
            AND IsAvailable = 0
            ORDER BY CheckTime DESC
            """
            
            cursor.execute(query)
            
            for row in cursor.fetchall():
                alerts.append({
                    'alert_type': 'SERVER_DOWN',
                    'severity': 'CRITICAL',
                    'server_name': row.ServerName,
                    'message': f"Server {row.ServerName} is unavailable: {row.ErrorMessage}",
                    'metric_value': 0,
                    'timestamp': row.CheckTime.isoformat() if row.CheckTime else None
                })
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to check server availability alerts: {e}")
        
        return alerts
    
    def check_performance_alerts(self) -> List[Dict]:
        """Check for performance threshold violations"""
        alerts = []
        
        try:
            conn = pyodbc.connect(self.monitoring_conn_string)
            cursor = conn.cursor()
            
            # Check CPU usage
            if 'cpu_percent' in self.thresholds:
                query = """
                SELECT TOP 10
                    ServerName,
                    CPUUsagePercent,
                    CollectionTime
                FROM PerformanceMetrics
                WHERE CollectionTime >= DATEADD(MINUTE, -5, GETDATE())
                AND CPUUsagePercent > ?
                ORDER BY CollectionTime DESC
                """
                
                cursor.execute(query, self.thresholds['cpu_percent'])
                
                for row in cursor.fetchall():
                    alerts.append({
                        'alert_type': 'HIGH_CPU',
                        'severity': 'HIGH' if row.CPUUsagePercent > 90 else 'MEDIUM',
                        'server_name': row.ServerName,
                        'message': f"High CPU usage on {row.ServerName}: {row.CPUUsagePercent}%",
                        'metric_value': row.CPUUsagePercent,
                        'timestamp': row.CollectionTime.isoformat() if row.CollectionTime else None
                    })
            
            # Check Memory usage
            if 'memory_percent' in self.thresholds:
                query = """
                SELECT TOP 10
                    ServerName,
                    MemoryUsagePercent,
                    CollectionTime
                FROM PerformanceMetrics
                WHERE CollectionTime >= DATEADD(MINUTE, -5, GETDATE())
                AND MemoryUsagePercent > ?
                ORDER BY CollectionTime DESC
                """
                
                cursor.execute(query, self.thresholds['memory_percent'])
                
                for row in cursor.fetchall():
                    alerts.append({
                        'alert_type': 'HIGH_MEMORY',
                        'severity': 'HIGH' if row.MemoryUsagePercent > 95 else 'MEDIUM',
                        'server_name': row.ServerName,
                        'message': f"High memory usage on {row.ServerName}: {row.MemoryUsagePercent}%",
                        'metric_value': row.MemoryUsagePercent,
                        'timestamp': row.CollectionTime.isoformat() if row.CollectionTime else None
                    })
            
            # Check Blocked Sessions
            if 'blocked_sessions' in self.thresholds:
                query = """
                SELECT TOP 10
                    ServerName,
                    BlockedSessions,
                    CollectionTime
                FROM PerformanceMetrics
                WHERE CollectionTime >= DATEADD(MINUTE, -5, GETDATE())
                AND BlockedSessions > ?
                ORDER BY CollectionTime DESC
                """
                
                cursor.execute(query, self.thresholds['blocked_sessions'])
                
                for row in cursor.fetchall():
                    alerts.append({
                        'alert_type': 'BLOCKED_SESSIONS',
                        'severity': 'HIGH',
                        'server_name': row.ServerName,
                        'message': f"Blocked sessions detected on {row.ServerName}: {row.BlockedSessions} sessions",
                        'metric_value': row.BlockedSessions,
                        'timestamp': row.CollectionTime.isoformat() if row.CollectionTime else None
                    })
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to check performance alerts: {e}")
        
        return alerts
    
    def check_database_alerts(self) -> List[Dict]:
        """Check for database availability issues"""
        alerts = []
        
        try:
            conn = pyodbc.connect(self.monitoring_conn_string)
            cursor = conn.cursor()
            
            # Check for offline databases
            query = """
            SELECT 
                ServerName,
                DatabaseName,
                State,
                CheckTime
            FROM DatabaseAvailability
            WHERE CheckTime >= DATEADD(MINUTE, -5, GETDATE())
            AND State != 'ONLINE'
            ORDER BY CheckTime DESC
            """
            
            cursor.execute(query)
            
            for row in cursor.fetchall():
                alerts.append({
                    'alert_type': 'DATABASE_OFFLINE',
                    'severity': 'HIGH',
                    'server_name': row.ServerName,
                    'message': f"Database {row.DatabaseName} on {row.ServerName} is {row.State}",
                    'metric_value': 0,
                    'timestamp': row.CheckTime.isoformat() if row.CheckTime else None
                })
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to check database alerts: {e}")
        
        return alerts
    
    def save_alert(self, alert: Dict):
        """Save alert to database"""
        try:
            conn = pyodbc.connect(self.monitoring_conn_string)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO AlertHistory (
                    ServerName, AlertName, AlertMessage, Severity,
                    MetricValue, IsResolved, TriggeredTime
                )
                VALUES (?, ?, ?, ?, ?, 0, GETDATE())
            """, (
                alert['server_name'],
                alert['alert_type'],
                alert['message'],
                alert['severity'],
                alert['metric_value']
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")
    
    def send_email_alert(self, alerts: List[Dict]):
        """Send email notification for alerts"""
        if not self.email_config.get('enabled', False):
            return
        
        if not alerts:
            return
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"SQL Server Monitoring Alert - {len(alerts)} issue(s) detected"
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            
            # Create HTML body
            html_body = self._create_alert_email_html(alerts)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)
            
            logger.info(f"✓ Sent email alert for {len(alerts)} issue(s)")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _create_alert_email_html(self, alerts: List[Dict]) -> str:
        """Create HTML email body for alerts"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .alert { padding: 10px; margin: 10px 0; border-left: 4px solid; }
                .critical { border-color: #dc3545; background-color: #f8d7da; }
                .high { border-color: #fd7e14; background-color: #fff3cd; }
                .medium { border-color: #ffc107; background-color: #fff3cd; }
                .low { border-color: #17a2b8; background-color: #d1ecf1; }
            </style>
        </head>
        <body>
            <h2>SQL Server Monitoring Alerts</h2>
            <p>The following issues have been detected:</p>
        """
        
        for alert in alerts:
            severity_class = alert['severity'].lower()
            html += f"""
            <div class="alert {severity_class}">
                <strong>{alert['severity']}</strong> - {alert['alert_type']}<br>
                <strong>Server:</strong> {alert['server_name']}<br>
                <strong>Message:</strong> {alert['message']}<br>
                <strong>Time:</strong> {alert['timestamp']}<br>
            </div>
            """
        
        html += """
            <p>Please investigate these issues as soon as possible.</p>
        </body>
        </html>
        """
        
        return html
    
    def run_alert_check(self):
        """Run complete alert check cycle"""
        logger.info("\n=== SQL Server Alert Check ===")
        
        all_alerts = []
        
        # Check server availability
        server_alerts = self.check_server_availability_alerts()
        all_alerts.extend(server_alerts)
        if server_alerts:
            logger.warning(f"Found {len(server_alerts)} server availability alert(s)")
        
        # Check performance metrics
        perf_alerts = self.check_performance_alerts()
        all_alerts.extend(perf_alerts)
        if perf_alerts:
            logger.warning(f"Found {len(perf_alerts)} performance alert(s)")
        
        # Check database availability
        db_alerts = self.check_database_alerts()
        all_alerts.extend(db_alerts)
        if db_alerts:
            logger.warning(f"Found {len(db_alerts)} database alert(s)")
        
        # Save and send alerts
        if all_alerts:
            logger.warning(f"Total alerts: {len(all_alerts)}")
            for alert in all_alerts:
                self.save_alert(alert)
                logger.warning(f"  [{alert['severity']}] {alert['message']}")
            
            self.send_email_alert(all_alerts)
        else:
            logger.info("✓ No alerts detected - all systems normal")
        
        logger.info("=== Alert Check Complete ===\n")


def main():
    """Main execution function"""
    try:
        alert_system = AlertSystem('monitoring_config.json')
        alert_system.run_alert_check()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")


if __name__ == "__main__":
    main()

# Made with Bob