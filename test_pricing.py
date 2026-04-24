# test_pricing.py
from pricing_engine import PricingEngine
from pdf_processor import DocumentExtractor
import asyncio

async def test():
    # Extract first
    extractor = DocumentExtractor()
    tender_data = await extractor.extract("workspace/tenders/1/RFQ Document PR10115496 for Cleaning Services East London Office.pdf")
    
    print(f"Sector: {tender_data['sector']}")
    print(f"Workers: {tender_data['workforce']['total_workers']}")
    print(f"Duration: {tender_data['duration']['display']}")
    
    # Calculate pricing
    engine = PricingEngine()
    pricing = engine.calculate(tender_data, {}, {'final_price': 0})
    
    print(f"\nMonthly Cost: R {pricing['total_monthly']:,.2f}")
    print(f"Contract Value: R {pricing['total_contract_value']:,.2f}")
    print(f"Breakdown: {pricing['breakdown']}")

asyncio.run(test())
