import os
import time
import json
import logging
import re
from datetime import datetime
import sys
import os

# Add parent directory to sys.path to import intelligence
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from intelligence.pricing_intelligence import PricingIntelligence

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

# -----------------------
# CONFIG
# -----------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "workspace", "tender_database")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "scraper.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

PROVINCES = [
    "Gauteng", "Western Cape", "KwaZulu-Natal",
    "Eastern Cape", "Limpopo", "Mpumalanga",
    "Free State", "North West", "Northern Cape"
]

KEYWORDS = {
    "construction": ["build", "construct", "civil", "road", "repair"],
    "cleaning": ["clean", "sanitize", "waste"],
    "security": ["security", "guard", "surveillance"],
    "electrical": ["electrical", "cable", "power"],
}

# -----------------------
# UTILS
# -----------------------

def detect_province(text):
    text = text.lower()
    for p in PROVINCES:
        if p.lower() in text:
            return p
    return "Unknown"


def detect_sector(text):
    text = text.lower()
    for sector, words in KEYWORDS.items():
        if any(w in text for w in words):
            return sector
    return "general"


# -----------------------
# SCRAPER CLASS
# -----------------------

class TenderScraper:

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        self.wait = WebDriverWait(self.driver, 20)

    def scrape(self, max_pages=3):
        self.driver.get("https://www.etenders.gov.za/Home/opportunities?id=1")
        time.sleep(5)

        results = []

        for page in range(max_pages):
            logging.info(f"Page {page+1}")

            rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) < 5:
                        continue

                    ref = cells[1].text.strip()
                    category = cells[2].text.strip()
                    title = cells[3].text.strip()
                    closing = cells[4].text.strip()

                    full_text = f"{title} {category}"

                    record = {
                        "reference": ref,
                        "title": title,
                        "province": detect_province(full_text),
                        "sector": detect_sector(full_text),
                        "closing_date": closing,
                        "source": "etenders",
                        "scraped_at": datetime.utcnow().isoformat()
                    }

                    results.append(record)

                except Exception as e:
                    logging.warning(f"Row error: {e}")

            # next page
            try:
                next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.paginate_button.next:not(.disabled)")
                next_btn.click()
                time.sleep(3)
            except:
                break

        return results

    def save(self, data):
        path = os.path.join(DATA_DIR, "tenders.json")

        if os.path.exists(path):
            with open(path) as f:
                existing = json.load(f)
        else:
            existing = []

        combined = existing + data

        # remove duplicates
        unique = {d["reference"]: d for d in combined}
        final = list(unique.values())

        with open(path, "w") as f:
            json.dump(final, f, indent=2)

        logging.info(f"Saved {len(final)} tenders")
        
        # Trigger pricing intelligence update
        insights_path = os.path.join(DATA_DIR, "pricing_insights.json")
        pi = PricingIntelligence(path, insights_path)
        pi.analyze()
        logging.info("Updated pricing insights.")

    def run(self):
        try:
            data = self.scrape()
            self.save(data)
        finally:
            self.driver.quit()


if __name__ == "__main__":
    TenderScraper().run()