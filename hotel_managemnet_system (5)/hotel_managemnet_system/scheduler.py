import time
import requests
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('maintenance_scheduler')

def check_scheduled_tasks():
    """Check for any scheduled tasks that need to be processed."""
    try:
        # Call the process_scheduled_tasks endpoint
        url = "http://localhost:5000/process_scheduled_tasks"
        response = requests.get(url)
        
        if response.status_code == 200:
            logger.info(f"Successfully processed tasks: {response.text}")
        else:
            logger.error(f"Failed to process tasks: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error checking scheduled tasks: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting maintenance task scheduler")
    
    # Check interval in seconds (5 minutes)
    interval = 300
    
    try:
        while True:
            logger.info(f"Checking for scheduled tasks at {datetime.now()}")
            check_scheduled_tasks()
            logger.info(f"Sleeping for {interval} seconds")
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler stopped due to error: {str(e)}") 