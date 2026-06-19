"""
Automated Scheduler for SQL Server Monitoring
Runs data collection and alert checks on a schedule
"""

import schedule
import time
import logging
import sys
from datetime import datetime
from collect_sql_metrics import SQLServerMonitor
from alert_system import AlertSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MonitoringScheduler:
    """Automated monitoring scheduler"""
    
    def __init__(self, config_file: str = 'monitoring_config.json'):
        """Initialize scheduler"""
        self.monitor = SQLServerMonitor(config_file)
        self.alert_system = AlertSystem(config_file)
        self.config = self.monitor.config
    
    def collect_metrics_job(self):
        """Job to collect metrics"""
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting scheduled metrics collection at {datetime.now()}")
            logger.info(f"{'='*60}")
            
            self.monitor.collect_all_metrics()
            
            logger.info(f"{'='*60}")
            logger.info(f"Metrics collection completed at {datetime.now()}")
            logger.info(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"Error in metrics collection job: {e}")
    
    def check_alerts_job(self):
        """Job to check alerts"""
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting scheduled alert check at {datetime.now()}")
            logger.info(f"{'='*60}")
            
            self.alert_system.run_alert_check()
            
            logger.info(f"{'='*60}")
            logger.info(f"Alert check completed at {datetime.now()}")
            logger.info(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"Error in alert check job: {e}")
    
    def run(self):
        """Run the scheduler"""
        collection_interval = self.config.get('collection_interval_seconds', 30)
        
        logger.info("\n" + "="*60)
        logger.info("SQL Server Monitoring Scheduler Started")
        logger.info("="*60)
        logger.info(f"Collection Interval: {collection_interval} seconds")
        logger.info(f"Target Servers: {', '.join(self.config['target_servers'])}")
        logger.info("="*60 + "\n")
        
        # Schedule metrics collection
        schedule.every(collection_interval).seconds.do(self.collect_metrics_job)
        
        # Schedule alert checks (every 5 minutes)
        schedule.every(5).minutes.do(self.check_alerts_job)
        
        # Run initial collection immediately
        logger.info("Running initial metrics collection...")
        self.collect_metrics_job()
        
        logger.info("Running initial alert check...")
        self.check_alerts_job()
        
        logger.info("\nScheduler is now running. Press Ctrl+C to stop.\n")
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n\nScheduler stopped by user")
            logger.info("="*60)


def main():
    """Main execution function"""
    try:
        scheduler = MonitoringScheduler('monitoring_config.json')
        scheduler.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob