import json
import os

class WinScoreV2:
    def __init__(self, insights_path):
        self.insights_path = insights_path
        self.insights = self._load_insights()

    def _load_insights(self):
        if os.path.exists(self.insights_path):
            with open(self.insights_path, "r") as f:
                return json.load(f)
        return {}

    def calculate(self, price, sector, province, duration, workforce):
        # Base probability
        probability = 70.0
        issues = []
        suggestions = []
        risk_level = "Low"

        # Compare with sector average
        sector_avg = self.insights.get("sector_averages", {}).get(sector)
        if sector_avg:
            if price > sector_avg * 1.5:
                probability -= 20
                issues.append(f"Price is significantly higher than {sector} sector average.")
                suggestions.append("Consider reducing your margin to be more competitive.")
                risk_level = "High"
            elif price < sector_avg * 0.7:
                probability -= 10
                issues.append("Price might be too low, potentially raising concerns about delivery quality.")
                suggestions.append("Verify that all costs are covered in your pricing.")
                risk_level = "Medium"

        # Workforce check
        if workforce < 2:
            probability -= 15
            issues.append("Workforce size seems insufficient for most tenders.")
            suggestions.append("Consider partnering or increasing staff allocation.")
            risk_level = "Medium" if risk_level == "Low" else "High"

        # Duration check
        if duration < 1:
            probability -= 5
            issues.append("Duration is very short, which may impact project stability.")
            suggestions.append("Clarify if the timeline is realistic.")

        # Final constraints
        probability = max(5, min(95, probability))
        
        if probability < 40:
            risk_level = "High"
        elif probability < 70:
            risk_level = "Medium"

        return {
            "win_probability": f"{round(probability, 1)}%",
            "risk_level": risk_level,
            "issues": issues,
            "suggestions": suggestions
        }

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INSIGHTS_JSON = os.path.join(BASE_DIR, "workspace", "tender_database", "pricing_insights.json")
    
    ws = WinScoreV2(INSIGHTS_JSON)
    # Example calculation
    print(ws.calculate(500000, "construction", "Gauteng", 12, 10))
