# debug_pdf.py (save this)
import asyncio
from pdf_processor import DocumentExtractor

async def test():
    extractor = DocumentExtractor()
    
    # Use the PDF file!
    result = await extractor.extract("workspace/tenders/1/RFQ Document PR10115496 for Cleaning Services East London Office.pdf")
    
    print("="*60)
    print("PDF EXTRACTION RESULTS")
    print("="*60)
    print(f"Sector: {result.get('sector')}")
    print(f"Workers: {result.get('workforce', {}).get('total_workers')}")
    print(f"Duration: {result.get('duration', {}).get('display')}")
    print(f"\nFirst 1000 chars of extracted text:")
    print(result.get('raw_text', '')[:1000])
    print("="*60)

asyncio.run(test())
