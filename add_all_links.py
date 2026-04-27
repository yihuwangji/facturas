import pdfplumber, json, re, sys, os, shutil
sys.stdout.reconfigure(encoding='utf-8')

DATA_JS = r'C:\Users\Administrador\Desktop\facturas\data.js'
PDFS_DIR = r'C:\Users\Administrador\Desktop\facturas\pdfs'
BASE_URL = 'https://yihuwangji.github.io/facturas/pdfs/'

with open(DATA_JS, 'r', encoding='utf-8') as f:
    content = f.read()
m = re.search(r'var SEED_DATA\s*=\s*(\{.*\});', content, re.DOTALL)
data = json.loads(m.group(1))
invoices = data['invoices']
next_id = data['nextId']

# Parse PRINCESALISIMO PDFs for totals
def parse_princesa_pdf(pdf_path):
    """Extract total from a PRINCESALISIMO invoice PDF"""
    pdf = pdfplumber.open(pdf_path)
    full_text = ""
    for page in pdf.pages:
        t = page.extract_text()
        if t:
            full_text += t + "\n"
    
    # Extract invoice number
    num_match = re.search(r'Factura:\s*(\d+)', full_text)
    num = num_match.group(1) if num_match else ""
    
    # Extract total - look for the last total line
    # Pattern: total amount at end, like "4168,692" or "917,664"
    total_match = re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2,3})\s*(?:13)?$', full_text, re.MULTILINE)
    
    # Also try to find the Base/IVA/Total block
    base_match = re.search(r'21,000%\s+([\d.,]+)', full_text)
    
    # Get total from "TOTAL" or the largest number near end
    # Look for pattern like "4.168,692" or "917,664"
    amounts = re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2,3})', full_text)
    
    # The total is typically the largest amount with IVA
    # Let's find the summary block at end
    lines = full_text.split('\n')
    total = 0
    base = 0
    iva = 0
    
    for i, line in enumerate(lines):
        # Look for the IVA summary block
        if '21,000%' in line and '723' in line or '159' in line or '80' in line:
            parts = line.split()
            for j, p in enumerate(parts):
                if '21,000%' == p and j+1 < len(parts):
                    try:
                        base = float(parts[j+1].replace('.', '').replace(',', '.'))
                    except:
                        pass
                if '21,000%' == p and j+2 < len(parts):
                    try:
                        iva = float(parts[j+2].replace('.', '').replace(',', '.'))
                    except:
                        pass
    
    # Find total from last significant number
    if total_match:
        try:
            total = float(total_match[-1].replace('.', '').replace(',', '.'))
        except:
            pass
    
    # Fallback: extract from text more carefully
    # The total is on the same line as base + iva amounts
    summary_match = re.search(r'21,000%\s+([\d.,]+)\s+21,000%\s+([\d.,]+)\s+[\d.,]+%\s+[\d.,]+\s+([\d.,]+)', full_text)
    if summary_match:
        base = float(summary_match.group(1).replace('.', '').replace(',', '.'))
        iva = float(summary_match.group(2).replace('.', '').replace(',', '.'))
        total = base + iva
    
    return {'num': num, 'base': base, 'iva': iva, 'total': round(total, 2)}

# Parse new PRINCESALISIMO invoices
new_invoices = []
pdf_paths = [
    r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205397_2026-04-20.pdf',
    r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205398_2026-04-20.pdf',
    r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205399_2026-04-20.pdf',
    r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205400_2026-04-20.pdf',
    r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205401_2026-04-20.pdf',
    r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205402_2026-04-20.pdf',
]

# Also parse the FVA2604156 income invoice
fva_path = r'C:\Users\Administrador\Desktop\发票\3月\Factura_FVA2604156_.pdf'

# Parse QUALIANZA 2206659603
qual_path = r'C:\Users\Administrador\Desktop\发票\4月\QUALIANZA_2206659603_2026-04-20.pdf'

print("=== Parsing PRINCESALISIMO invoices ===")
for pdf_path in pdf_paths:
    info = parse_princesa_pdf(pdf_path)
    print(f"  num={info['num']} base={info['base']} iva={info['iva']} total={info['total']}")
    
    # Copy PDF to pdfs/ dir
    dst_name = f"PRINCESALISIMO_{info['num']}.pdf"
    target = os.path.join(PDFS_DIR, dst_name)
    if not os.path.exists(target):
        shutil.copy2(pdf_path, target)
    
    new_inv = {
        "id": next_id,
        "num": info['num'],
        "date": "2026-04-20",
        "due": "2026-05-20",
        "supplier": "PRINCESALISIMO S.L.U.",
        "nif": "B46350534",
        "desc": "BEBIDAS Y REFRESCOS",
        "base": info['base'],
        "ivaRate": 21,
        "ivaAmt": info['iva'],
        "total": info['total'],
        "payMethod": "transferencia",
        "bankAmt": info['total'],
        "cashAmt": 0,
        "payDate": "",
        "notes": "",
        "category": "",
        "type": "expense",
        "client": "",
        "irpfRate": 0,
        "irpfAmt": 0,
        "pdfFile": BASE_URL + dst_name,
        "createdAt": "2026-04-27T16:00:00.000Z"
    }
    new_invoices.append(new_inv)
    next_id += 1

# Parse FVA2604156 - income invoice
print("\n=== Parsing FVA2604156 ===")
try:
    pdf = pdfplumber.open(fva_path)
    full_text = ""
    for page in pdf.pages:
        t = page.extract_text()
        if t:
            full_text += t + "\n"
    
    # This is a sales invoice (income)
    # FVA2604156, date 20/03/2026, total 463.59 EUR
    # Base: 383.13, IVA 21%: 80.46, Total: 463.59
    base_fva = 383.13
    iva_fva = 80.46
    total_fva = 463.59
    
    dst_name = "EUROFAMILIA_FVA2604156.pdf"
    target = os.path.join(PDFS_DIR, dst_name)
    if not os.path.exists(target):
        shutil.copy2(fva_path, target)
    
    new_inv = {
        "id": next_id,
        "num": "FVA2604156",
        "date": "2026-03-20",
        "due": "2026-04-19",
        "supplier": "",
        "nif": "",
        "desc": "HORNILLO DE GAS PORTATIL",
        "base": base_fva,
        "ivaRate": 21,
        "ivaAmt": iva_fva,
        "total": total_fva,
        "payMethod": "transferencia",
        "bankAmt": total_fva,
        "cashAmt": 0,
        "payDate": "",
        "notes": "",
        "category": "",
        "type": "income",
        "client": "ANA",
        "irpfRate": 0,
        "irpfAmt": 0,
        "pdfFile": BASE_URL + dst_name,
        "createdAt": "2026-04-27T16:00:00.000Z"
    }
    new_invoices.append(new_inv)
    next_id += 1
    print(f"  num=FVA2604156 base={base_fva} iva={iva_fva} total={total_fva}")
except Exception as e:
    print(f"  Error: {e}")

# Parse QUALIANZA 2206659603 - need full text
print("\n=== Parsing QUALIANZA 2206659603 ===")
try:
    pdf = pdfplumber.open(qual_path)
    full_text = ""
    for page in pdf.pages:
        t = page.extract_text()
        if t:
            full_text += t + "\n"
    print(f"  Text length: {len(full_text)}")
    # Look for total
    amounts = re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2})', full_text)
    print(f"  Amounts found: {amounts[-5:] if amounts else 'none'}")
    
    # Update id=322 (MISSING-322) with correct num and add PDF
    for inv in data['invoices']:
        if inv['id'] == 322:
            inv['num'] = '2206659603'
            inv['desc'] = 'PRODUCTOS ALIMENTARIOS'
            # Try to find total amount
            # From the PDF text, we need to extract the total
            # Let's check for a number pattern like "1.234,56"
            total_match = re.findall(r'Total.*?([\d.,]+)', full_text, re.IGNORECASE)
            print(f"  Total matches: {total_match}")
            break
except Exception as e:
    print(f"  Error: {e}")

# Add new invoices to data
data['invoices'].extend(new_invoices)
data['nextId'] = next_id
data['version'] = '2026-04-27-v4'

# Write back
new_json = json.dumps(data, ensure_ascii=False, indent=2)
new_content = f"// Generated 2026-04-27 18:00\nvar SEED_DATA = {new_json};"
with open(DATA_JS, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n=== SUMMARY ===")
print(f"New invoices added: {len(new_invoices)}")
for inv in new_invoices:
    print(f"  id={inv['id']} num={inv['num']} total={inv['total']} type={inv['type']}")
print(f"Total invoices now: {len(data['invoices'])}")
print(f"Next ID: {next_id}")

# Count pdfFile stats
with_pdf = sum(1 for inv in data['invoices'] if inv.get('pdfFile'))
print(f"Invoices with PDF link: {with_pdf}")
print(f"Invoices without PDF link: {len(data['invoices']) - with_pdf}")
