import json
import os
from collections import defaultdict

class PricingIntelligence:
    def __init__(self, tenders_path, insights_path):
        self.tenders_path = tenders_path
        self.insights_path = insights_path

    def analyze(self):
        if not os.path.exists(self.tenders_path):
            return {"error": "tenders.json not found"}

        with open(self.tenders_path, "r") as f:
            tenders = json.load(f)

        sector_totals = defaultdict(list)
        province_totals = defaultdict(list)

        for tender in tenders:
            sector = tender.get("sector", "general")
            province = tender.get("province", "Unknown")
            value = tender.get("estimated_value")

            if value and isinstance(value, (int, float)):
                sector_totals[sector].append(value)
                province_totals[province].append(value)

        insights = {
            "sector_averages": {s: sum(v)/len(v) for s, v in sector_totals.items() if v},
            "province_averages": {p: sum(v)/len(v) for p, v in province_totals.items() if v},
            "total_tenders": len(tenders),
            "last_updated": os.path.getmtime(self.tenders_path) if os.path.exists(self.tenders_path) else None
        }

        with open(self.insights_path, "w") as f:
            json.dump(insights, f, indent=2)

        return insights

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TENDERS_JSON = os.path.join(BASE_DIR, "workspace", "tender_database", "tenders.json")
    INSIGHTS_JSON = os.path.join(BASE_DIR, "workspace", "tender_database", "pricing_insights.json")
    
    pi = PricingIntelligence(TENDERS_JSON, INSIGHTS_JSON)
    print(pi.analyze())
