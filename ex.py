import sys
sys.path.insert(0, r'C:\Users\Administrador\Desktop\facturas')
import json

pdf_path = r'C:\Users\Administrador\Desktop\facturas\invoice_new.pdf'

try:
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    print(f"Pages: {len(reader.pages)}")
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        print(f"\n--- Page {i+1} ---")
        print(text)
except Exception as e:
    print(f"pypdf error: {e}")
    try:
        import fitz
        doc = fitz.open(pdf_path)
        print(f"Pages: {len(doc)}")
        for i, page in enumerate(doc):
            text = page.get_text()
            print(f"\n--- Page {i+1} ---")
            print(text)
    except Exception as e2:
        print(f"fitz error: {e2}")