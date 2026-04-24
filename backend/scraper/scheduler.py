import time
import os
import subprocess
import logging
from datetime import datetime

# Configure logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "scheduler.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_scraper():
    logging.info("Starting daily scraper run...")
    scraper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraper_production.py")
    try:
        # Run the scraper as a subprocess
        result = subprocess.run(["python", scraper_path], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info("Scraper finished successfully.")
        else:
            logging.error(f"Scraper failed with error: {result.stderr}")
    except Exception as e:
        logging.error(f"Scheduler encountered an error: {e}")

def main():
    logging.info("Tender System Scheduler started.")
    while True:
        # Check if it's 2 AM (typical time for daily scrapers)
        now = datetime.now()
        if now.hour == 2 and now.minute == 0:
            run_scraper()
            # Sleep for 61 seconds to avoid multiple runs in the same minute
            time.sleep(61)
        
        # Check every minute
        time.sleep(60)

if __name__ == "__main__":
    main()
