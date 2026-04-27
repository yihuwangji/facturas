import json, re, os

# Read data.js to get invoice data
with open(r'C:\Users\Administrador\Desktop\facturas\data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JSON from data.js
match = re.search(r'var SEED_DATA\s*=\s*(\{.*\});', content, re.DOTALL)
data = json.loads(match.group(1))
invoices = data['invoices']

# Build a map of invoice num -> invoice
invoice_map = {}
for inv in invoices:
    if inv.get('num'):
        key = inv['num'].strip()
        invoice_map[key] = inv

print(f'Total invoices in data.js: {len(invoices)}')
print(f'Invoices with num field: {len(invoice_map)}')
print()

# Also build supplier-based maps for fuzzy matching
supplier_lower_map = {}
for inv in invoices:
    s = inv.get('supplier', '') or inv.get('client', '')
    if s:
        supplier_lower_map.setdefault(s.lower(), []).append(inv)

# Scan PDF folders
pdf_dirs = [
    r'C:\Users\Administrador\Desktop\发票\3月',
    r'C:\Users\Administrador\Desktop\发票\4月',
    r'C:\Users\Administrador\Desktop\facturas\pdfs'
]

# Collect all PDFs with their paths
all_pdfs = []
for d in pdf_dirs:
    if os.path.exists(d):
        for f in os.listdir(d):
            if f.lower().endswith('.pdf'):
                all_pdfs.append((f, os.path.join(d, f)))

print(f'Total PDF files found: {len(all_pdfs)}')
print()

# Try to match PDFs to invoices by extracting invoice numbers from filenames
matches = []
unmatched_pdfs = []

for fname, fpath in all_pdfs:
    matched = False
    
    # Pattern: extract all long numbers from filename
    numbers = re.findall(r'(?:^|[_\-\s])(\d{6,})(?:[_\-\s.]|$)', fname)
    # Also try numbers at start
    numbers2 = re.findall(r'^(\d+)_', fname)
    all_nums = list(set(numbers + numbers2))
    
    for num in all_nums:
        if num in invoice_map:
            inv = invoice_map[num]
            matches.append({
                'pdf_file': fname,
                'pdf_path': fpath,
                'invoice_id': inv['id'],
                'invoice_num': inv['num'],
                'supplier': inv.get('supplier', inv.get('client', '')),
                'type': inv.get('type', ''),
                'already_has_link': bool(inv.get('pdfFile'))
            })
            matched = True
            break
    
    if not matched:
        # Try FVA pattern
        fva_match = re.search(r'FVA(\d+)', fname)
        if fva_match:
            num_key = 'FVA' + fva_match.group(1)
            if num_key in invoice_map:
                inv = invoice_map[num_key]
                matches.append({
                    'pdf_file': fname,
                    'pdf_path': fpath,
                    'invoice_id': inv['id'],
                    'invoice_num': inv['num'],
                    'supplier': inv.get('supplier', ''),
                    'type': inv.get('type', ''),
                    'already_has_link': bool(inv.get('pdfFile'))
                })
                matched = True

        # Try FVV pattern
        if not matched:
            fvv_match = re.search(r'FVV(\d+)', fname)
            if fvv_match:
                num_key = 'FVV' + fvv_match.group(1)
                if num_key in invoice_map:
                    inv = invoice_map[num_key]
                    matches.append({
                        'pdf_file': fname,
                        'pdf_path': fpath,
                        'invoice_id': inv['id'],
                        'invoice_num': inv['num'],
                        'supplier': inv.get('supplier', ''),
                        'type': inv.get('type', ''),
                        'already_has_link': bool(inv.get('pdfFile'))
                    })
                    matched = True

        # Try EE pattern for GOYVAL
        if not matched:
            ee_match = re.search(r'EE(\d+)', fname)
            if ee_match:
                num_key = 'EE' + ee_match.group(1)
                if num_key in invoice_map:
                    inv = invoice_map[num_key]
                    matches.append({
                        'pdf_file': fname,
                        'pdf_path': fpath,
                        'invoice_id': inv['id'],
                        'invoice_num': inv['num'],
                        'supplier': inv.get('supplier', ''),
                        'type': inv.get('type', ''),
                        'already_has_link': bool(inv.get('pdfFile'))
                    })
                    matched = True

        # Try 23Z pattern for BEMALU
        if not matched:
            z_match = re.search(r'23Z-(\d+)', fname)
            if z_match:
                num_key = '23Z-' + z_match.group(1)
                if num_key in invoice_map:
                    inv = invoice_map[num_key]
                    matches.append({
                        'pdf_file': fname,
                        'pdf_path': fpath,
                        'invoice_id': inv['id'],
                        'invoice_num': inv['num'],
                        'supplier': inv.get('supplier', ''),
                        'type': inv.get('type', ''),
                        'already_has_link': bool(inv.get('pdfFile'))
                    })
                    matched = True

        # Try Y pattern for LogiTrade (Y26002069)
        if not matched:
            y_match = re.search(r'Y(\d{7,})', fname)
            if y_match:
                num_key = 'Y' + y_match.group(1)
                if num_key in invoice_map:
                    inv = invoice_map[num_key]
                    matches.append({
                        'pdf_file': fname,
                        'pdf_path': fpath,
                        'invoice_id': inv['id'],
                        'invoice_num': inv['num'],
                        'supplier': inv.get('supplier', ''),
                        'type': inv.get('type', ''),
                        'already_has_link': bool(inv.get('pdfFile'))
                    })
                    matched = True

    if not matched:
        unmatched_pdfs.append((fname, fpath))

print('=== MATCHED PDFs ===')
needs_link = []
for m in matches:
    status = 'HAS LINK' if m['already_has_link'] else 'NEEDS LINK'
    print(f"  [{status}] {m['pdf_file']} -> id={m['invoice_id']} num={m['invoice_num']} ({m['supplier']})")
    if not m['already_has_link']:
        needs_link.append(m)

print()
print(f'Total matched: {len(matches)}')
print(f'Need link: {len(needs_link)}')
print(f'Already have link: {len(matches) - len(needs_link)}')
print()
print('=== UNMATCHED PDFs ===')
for fname, fpath in unmatched_pdfs:
    print(f'  {fname}')

# Print all invoice nums for reference (to help manual matching)
print()
print('=== All invoice nums in data.js (no pdfFile) ===')
for inv in invoices:
    if not inv.get('pdfFile') and inv.get('num'):
        print(f"  id={inv['id']} num={inv['num']} supplier={inv.get('supplier', inv.get('client', ''))} date={inv.get('date', '')}")
