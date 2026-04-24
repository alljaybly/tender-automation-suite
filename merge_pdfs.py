from PyPDF2 import PdfMerger
import glob
import sys

merger = PdfMerger()

# Get all PDF files
pdf_files = sorted(glob.glob('*.pdf'))

if not pdf_files:
    print("No PDF files found!")
    sys.exit(1)

print(f"Merging {len(pdf_files)} PDF files:")
for pdf in pdf_files:
    print(f"  - {pdf}")
    merger.append(pdf)

# Save merged file
output_name = "COMPLETE_TENDER_PACKAGE.pdf"
merger.write(output_name)
merger.close()

print(f"\n✅ Success! Created: {output_name}")
print(f"Total size: {len(pdf_files)} documents merged")
