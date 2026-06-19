"""
Customer-Based SQL Server Monitoring Script
Monitors servers and databases for specific customers with dropdown selection
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
        logging.FileHandler('customer_monitoring.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CustomerMonitor:
    """Customer-specific SQL Server monitoring"""
    
    def __init__(self, config_file: str = 'monitoring_config.json', 
                 customer_config_file: str = 'customer_config.json'):
        """Initialize monitor with configuration"""
        self.config = self._load_config(config_file)
        self.customers = self._load_customer_config(customer_config_file)
        self.monitoring_conn_string = self._build_connection_string(
            self.config['monitoring_server']
        )
    
    def _load_config(self, config_file: str) -> Dict:
        """Load monitoring configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), config_file)
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_file}")
            return {
                "monitoring_server": {
                    "server": "localhost",
                    "database": "SQLServerMonitoring",
                    "use_windows_auth": True
                }
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    def _load_customer_config(self, customer_config_file: str) -> List[Dict]:
        """Load customer configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), customer_config_file)
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('customers', [])
        except FileNotFoundError:
            logger.error(f"Customer config file not found: {customer_config_file}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in customer config file: {e}")
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
    
    def get_top_customers(self, limit: int = 10) -> List[Dict]:
        """Get top N customers"""
        return self.customers[:limit]
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict]:
        """Get customer by ID"""
        for customer in self.customers:
            if customer['customer_id'] == customer_id:
                return customer
        return None
    
    def get_customer_by_name(self, customer_name: str) -> Optional[Dict]:
        """Get customer by name"""
        for customer in self.customers:
            if customer['customer_name'].lower() == customer_name.lower():
                return customer
        return None
    
    def test_server_availability(self, server_instance: str, customer_name: str) -> Dict[str, Any]:
        """Test SQL Server availability for a customer's server"""
        start_time = time.time()
        
        try:
            conn_string = self._build_connection_string({
                'server': server_instance, 
                'use_windows_auth': True
            })
            conn = pyodbc.connect(conn_string, timeout=5)
            cursor = conn.cursor()
            
            # Get version info
            cursor.execute("SELECT @@VERSION AS Version, SERVERPROPERTY('ProductVersion') AS ProductVersion")
            row = cursor.fetchone()
            
            response_time = (time.time() - start_time) * 1000
            
            result = {
                'customer_name': customer_name,
                'server_instance': server_instance,
                'is_available': True,
                'response_time_ms': round(response_time, 2),
                'version': row.Version if row else None,
                'product_version': row.ProductVersion if row else None,
                'error_message': None,
                'check_time': datetime.now().isoformat()
            }
            
            cursor.close()
            conn.close()
            
            logger.info(f"✓ [{customer_name}] Server {server_instance} is ONLINE (Response: {result['response_time_ms']}ms)")
            return result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"✗ [{customer_name}] Server {server_instance} is OFFLINE: {str(e)}")
            return {
                'customer_name': customer_name,
                'server_instance': server_instance,
                'is_available': False,
                'response_time_ms': round(response_time, 2),
                'version': None,
                'product_version': None,
                'error_message': str(e),
                'check_time': datetime.now().isoformat()
            }
    
    def get_database_availability(self, server_instance: str, customer_name: str) -> List[Dict[str, Any]]:
        """Get database availability for a customer's server"""
        try:
            conn_string = self._build_connection_string({
                'server': server_instance,
                'use_windows_auth': True
            })
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
                    'customer_name': customer_name,
                    'server_instance': server_instance,
                    'database_name': row.DatabaseName,
                    'state': row.State,
                    'is_online': row.State == 'ONLINE',
                    'recovery_model': row.RecoveryModel,
                    'size_mb': float(row.SizeMB) if row.SizeMB else 0,
                    'create_date': row.CreateDate.isoformat() if row.CreateDate else None,
                    'compatibility_level': row.CompatibilityLevel,
                    'check_time': datetime.now().isoformat()
                })
            
            cursor.close()
            conn.close()
            
            online_count = sum(1 for db in databases if db['is_online'])
            logger.info(f"  [{customer_name}] Found {len(databases)} databases ({online_count} online)")
            return databases
            
        except Exception as e:
            logger.error(f"Failed to get database availability for [{customer_name}] {server_instance}: {str(e)}")
            return []
    
    def monitor_customer(self, customer_id: int) -> Dict[str, Any]:
        """Monitor all servers and databases for a specific customer"""
        customer = self.get_customer_by_id(customer_id)
        
        if not customer:
            logger.error(f"Customer with ID {customer_id} not found")
            return {
                'error': f"Customer with ID {customer_id} not found",
                'customer_id': customer_id
            }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Monitoring Customer: {customer['customer_name']}")
        logger.info(f"Priority: {customer['priority']}")
        logger.info(f"Contact: {customer['contact_email']}")
        logger.info(f"{'='*60}\n")
        
        results = {
            'customer_id': customer['customer_id'],
            'customer_name': customer['customer_name'],
            'priority': customer['priority'],
            'contact_email': customer['contact_email'],
            'servers': [],
            'summary': {
                'total_servers': len(customer['servers']),
                'available_servers': 0,
                'unavailable_servers': 0,
                'total_databases': 0,
                'online_databases': 0,
                'offline_databases': 0
            },
            'check_time': datetime.now().isoformat()
        }
        
        for server in customer['servers']:
            logger.info(f"Checking server: {server['server_name']} ({server['description']})")
            
            # Test server availability
            availability = self.test_server_availability(
                server['server_instance'],
                customer['customer_name']
            )
            
            server_result = {
                'server_name': server['server_name'],
                'server_instance': server['server_instance'],
                'description': server['description'],
                'availability': availability,
                'databases': []
            }
            
            if availability['is_available']:
                results['summary']['available_servers'] += 1
                
                # Get database availability
                databases = self.get_database_availability(
                    server['server_instance'],
                    customer['customer_name']
                )
                
                server_result['databases'] = databases
                results['summary']['total_databases'] += len(databases)
                results['summary']['online_databases'] += sum(1 for db in databases if db['is_online'])
                results['summary']['offline_databases'] += sum(1 for db in databases if not db['is_online'])
            else:
                results['summary']['unavailable_servers'] += 1
            
            results['servers'].append(server_result)
            logger.info("")
        
        # Log summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Summary for {customer['customer_name']}:")
        logger.info(f"  Servers: {results['summary']['available_servers']}/{results['summary']['total_servers']} available")
        logger.info(f"  Databases: {results['summary']['online_databases']}/{results['summary']['total_databases']} online")
        logger.info(f"{'='*60}\n")
        
        return results
    
    def save_customer_monitoring_results(self, results: Dict[str, Any]):
        """Save customer monitoring results to database"""
        try:
            conn = pyodbc.connect(self.monitoring_conn_string)
            cursor = conn.cursor()
            
            # Save each server's availability
            for server in results['servers']:
                availability = server['availability']
                
                cursor.execute("""
                    INSERT INTO ServerAvailability (
                        ServerName, IsAvailable, ResponseTimeMs, Version, ProductVersion,
                        ErrorMessage, CheckTime
                    )
                    VALUES (?, ?, ?, ?, ?, ?, GETDATE())
                """, (
                    server['server_instance'],
                    availability['is_available'],
                    availability['response_time_ms'],
                    availability['version'],
                    availability['product_version'],
                    availability['error_message']
                ))
                
                # Save database availability
                for db in server['databases']:
                    cursor.execute("""
                        INSERT INTO DatabaseAvailability (
                            ServerName, DatabaseName, State, RecoveryModel,
                            SizeMB, CreateDate, CompatibilityLevel, CheckTime
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())
                    """, (
                        db['server_instance'],
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
            
            logger.info(f"✓ Saved monitoring results for customer: {results['customer_name']}")
            
        except Exception as e:
            logger.error(f"Failed to save monitoring results: {str(e)}")
    
    def list_all_customers(self):
        """List all customers with their server counts"""
        logger.info("\n" + "="*80)
        logger.info("TOP 10 CUSTOMERS")
        logger.info("="*80)
        
        for idx, customer in enumerate(self.get_top_customers(), 1):
            server_count = len(customer['servers'])
            logger.info(f"{idx:2d}. {customer['customer_name']:<30} | Priority: {customer['priority']:<8} | Servers: {server_count}")
        
        logger.info("="*80 + "\n")


def main():
    """Main execution function"""
    try:
        monitor = CustomerMonitor()
        
        # List all customers
        monitor.list_all_customers()
        
        # Interactive mode
        print("\nEnter Customer ID to monitor (1-10), or 'all' to monitor all customers, or 'exit' to quit:")
        
        while True:
            user_input = input("\nCustomer ID: ").strip().lower()
            
            if user_input == 'exit':
                logger.info("Exiting customer monitoring...")
                break
            
            if user_input == 'all':
                logger.info("\nMonitoring all customers...")
                for customer in monitor.get_top_customers():
                    results = monitor.monitor_customer(customer['customer_id'])
                    monitor.save_customer_monitoring_results(results)
                    time.sleep(2)  # Brief pause between customers
                continue
            
            try:
                customer_id = int(user_input)
                if 1 <= customer_id <= 10:
                    results = monitor.monitor_customer(customer_id)
                    monitor.save_customer_monitoring_results(results)
                else:
                    print("Please enter a number between 1 and 10")
            except ValueError:
                print("Invalid input. Please enter a number, 'all', or 'exit'")
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob