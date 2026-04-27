import pdfplumber, sys, json, re, os
sys.stdout.reconfigure(encoding='utf-8')

# Read all unmatched PRINCESALISIMO PDFs to extract invoice data
pdf_files = [
    r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205397_2026-04-20.pdf',
    r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205398_2026-04-20.pdf',
    r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205399_2026-04-20.pdf',
    r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205400_2026-04-20.pdf',
    r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205401_2026-04-20.pdf',
    r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205402_2026-04-20.pdf',
]

for pdf_path in pdf_files:
    try:
        pdf = pdfplumber.open(pdf_path)
        for page in pdf.pages[:1]:
            text = page.extract_text()
            if text:
                print(f"=== {os.path.basename(pdf_path)} ===")
                print(text[:800])
                print()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")

# Also read the QUALIANZA 2206659603
q_path = r'C:\Users\Administrador\Desktop\发票\4月\QUALIANZA_2206659603_2026-04-20.pdf'
try:
    pdf = pdfplumber.open(q_path)
    for page in pdf.pages[:1]:
        text = page.extract_text()
        if text:
            print(f"=== {os.path.basename(q_path)} ===")
            print(text[:800])
            print()
except Exception as e:
    print(f"Error: {e}")
