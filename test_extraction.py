# test_extraction.py (save this in tender_system folder)
import asyncio
from pdf_processor import DocumentExtractor

async def test():
    extractor = DocumentExtractor()
    result = await extractor.extract("workspace/tenders/1/RFQ_Document_PR10115496.docx")
    
    print("="*60)
    print("EXTRACTION RESULTS")
    print("="*60)
    print(f"Sector: {result.get('sector', 'NOT FOUND')}")
    print(f"Sub-type: {result.get('sub_type', 'NOT FOUND')}")
    print(f"Duration: {result.get('duration', {}).get('display', 'NOT FOUND')}")
    print(f"Workers (total): {result.get('workforce', {}).get('total_workers', 'NOT FOUND')}")
    print(f"Worker estimation method: {result.get('workforce', {}).get('estimation_method', 'NOT FOUND')}")
    print(f"Area: {result.get('scope', {}).get('area_sqm', 'NOT FOUND')}")
    print(f"Overall confidence: {result.get('_extraction_notes', {}).get('raw_confidence', 'NOT FOUND')}")
    print("="*60)

asyncio.run(test())
