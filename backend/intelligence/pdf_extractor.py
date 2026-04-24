import re
from typing import Dict, Optional

class TenderPDFExtractor:
    """
    Specialized extractor for tender-specific data like estimated value and duration.
    """
    
    def __init__(self):
        # Patterns for currency (Rand)
        self.currency_patterns = [
            r"R\s*(\d{1,3}(?:[,\s]\d{3})*(?:\.\d{2})?)",  # R 1,234,567.89 or R1234567
            r"estimated\s*value[:\s]*R?\s*(\d{1,3}(?:[,\s]\d{3})*(?:\.\d{2})?)",
            r"budget[:\s]*R?\s*(\d{1,3}(?:[,\s]\d{3})*(?:\.\d{2})?)",
            r"total\s*cost[:\s]*R?\s*(\d{1,3}(?:[,\s]\d{3})*(?:\.\d{2})?)",
        ]
        
        # Patterns for duration
        self.duration_patterns = [
            r"period\s*of\s*(\d+)\s*months?",
            r"duration\s*of\s*(\d+)\s*months?",
            r"contract\s*period[:\s]*(\d+)\s*months?",
            r"(\d+)\s*month\s*contract",
            r"period\s*of\s*(\d+)\s*years?",
            r"(\d+)\s*year\s*contract",
        ]

    def extract_estimated_value(self, text: str) -> Optional[float]:
        """Extract the highest Rand amount found that matches estimation patterns."""
        values = []
        for pattern in self.currency_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    val_str = match.group(1).replace(",", "").replace(" ", "")
                    values.append(float(val_str))
                except (ValueError, IndexError):
                    continue
        
        return max(values) if values else None

    def extract_duration(self, text: str) -> Dict:
        """Extract duration in months."""
        for pattern in self.duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = int(match.group(1))
                if "year" in match.group(0).lower():
                    return {"value": val * 12, "unit": "months", "original": f"{val} years"}
                return {"value": val, "unit": "months", "original": f"{val} months"}
        
        return {"value": 12, "unit": "months", "original": "12 months (default)"}

    def process_text(self, text: str) -> Dict:
        """Extract all intelligence fields from text."""
        return {
            "estimated_value": self.extract_estimated_value(text),
            "duration": self.extract_duration(text)
        }
