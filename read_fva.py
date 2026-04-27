import pdfplumber, sys
sys.stdout.reconfigure(encoding='utf-8')

pdf = pdfplumber.open(r'C:\Users\Administrador\Desktop\发票\3月\Factura_FVA2604156_.pdf')
for i, p in enumerate(pdf.pages[:2]):
    text = p.extract_text()
    if text:
        print(f"--- Page {i+1} ---")
        print(text[:1000])
