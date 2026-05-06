import subprocess
import sys

pdf_path = r"C:\Users\Administrador\.qclaw\media\inbound\扫描文件_20260504_161043---e9666115-f35f-46f1-ade7-ee881d5d564d.pdf"

# Check available libraries
for lib in ["pypdf", "pdfplumber", "fitz", "pymupdf"]:
    try:
        __import__(lib)
        print(f"OK: {lib}")
    except ImportError:
        print(f"MISSING: {lib}")

# Try pypdf first
try:
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    print(f"\nPages: {len(reader.pages)}")
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        print(f"\n--- Page {i+1} ---")
        print(text[:3000])
except Exception as e:
    print(f"pypdf failed: {e}")
    try:
        import fitz
        doc = fitz.open(pdf_path)
        print(f"\nPages: {len(doc)}")
        for i, page in enumerate(doc):
            text = page.get_text()
            print(f"\n--- Page {i+1} ---")
            print(text[:3000])
    except Exception as e2:
        print(f"fitz failed: {e2}")