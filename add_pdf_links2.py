import json, re, os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')

DATA_JS = r'C:\Users\Administrador\Desktop\facturas\data.js'
PDFS_DIR = r'C:\Users\Administrador\Desktop\facturas\pdfs'
BASE_URL = 'https://yihuwangji.github.io/facturas/pdfs/'

with open(DATA_JS, 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'var SEED_DATA\s*=\s*(\{.*\});', content, re.DOTALL)
data = json.loads(match.group(1))
invoices = data['invoices']

inv_by_id = {inv['id']: inv for inv in invoices}

# Additional mappings for the unmatched PDFs
extra_mappings = [
    # FVA2604156 - search for invoice with this num
    (r'C:\Users\Administrador\Desktop\发票\3月\Factura_FVA2604156_.pdf', 'FVA2604156.pdf', 'FVA2604156'),
    # MARBUENO 1-404 -> id=319 num=1/404
    (r'C:\Users\Administrador\Desktop\发票\4月\MARBUENO_1-404_2026-04-23.pdf', 'MARBUENO_1-404.pdf', '319'),
    # MARBUENO PROFORMA -> id=28 num=PROFORMA-727/1
    (r'C:\Users\Administrador\Desktop\发票\4月\MARBUENO_PROFORMA_727-1_2026-04-10.pdf', 'MARBUENO_PROFORMA-727-1.pdf', '28'),
    # PRINCESALISIMO 9205397-9205402 - these are NOT in data.js yet
    # QUALIANZA 2206659603 - might be id=322 (MISSING-322) or id=323
]

# Build num->id map
num_to_id = {}
for inv in invoices:
    if inv.get('num'):
        num_to_id[inv['num'].strip()] = inv['id']

# Also add some special lookups
special_lookups = {
    '319': 319,
    '28': 28,
}

updated = 0
copied = 0

for src, dst, lookup_key in extra_mappings:
    inv_id = None
    
    # Try numeric lookup first
    if lookup_key in special_lookups:
        inv_id = special_lookups[lookup_key]
    elif lookup_key in num_to_id:
        inv_id = num_to_id[lookup_key]
    elif lookup_key.isdigit():
        inv_id = int(lookup_key)
    
    if inv_id and inv_id in inv_by_id:
        inv = inv_by_id[inv_id]
        if not inv.get('pdfFile'):
            # Copy PDF
            if os.path.exists(src):
                target_path = os.path.join(PDFS_DIR, dst)
                if not os.path.exists(target_path):
                    shutil.copy2(src, target_path)
                    copied += 1
                inv['pdfFile'] = BASE_URL + dst
                updated += 1
                print(f"[OK] {dst} -> id={inv_id} num={inv.get('num','')}")
            else:
                print(f"[SKIP - source not found] {src}")
        else:
            print(f"[SKIP - already has link] {dst} -> id={inv_id}")
    else:
        print(f"[SKIP - no invoice match] {dst} (lookup: {lookup_key})")

# Now handle the PRINCESALISIMO 9205397-9205402 - these are NOT in the system yet
# Check if they exist as invoices
princesa_new = [9205397, 9205398, 9205399, 9205400, 9205401, 9205402]
found_princesa = []
for num in princesa_new:
    num_str = str(num)
    if num_str in num_to_id:
        found_princesa.append((num, num_to_id[num_str]))
    else:
        print(f"[INFO] PRINCESALISIMO {num_str} not found in data.js - may need to be imported")

if found_princesa:
    print(f"\n[FOUND] These PRINCESALISIMO invoices already exist:")
    for num, inv_id in found_princesa:
        inv = inv_by_id[inv_id]
        if not inv.get('pdfFile'):
            src = rf'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_{num}_2026-04-20.pdf'
            dst = f'PRINCESALISIMO_{num}.pdf'
            if os.path.exists(src):
                target_path = os.path.join(PDFS_DIR, dst)
                if not os.path.exists(target_path):
                    shutil.copy2(src, target_path)
                    copied += 1
                inv['pdfFile'] = BASE_URL + dst
                updated += 1
                print(f"  [OK] {dst} -> id={inv_id}")

# Handle QUALIANZA 2206659603
# Check id=322 (MISSING-322, QUALIANZA) and id=323 (MISSING-323, QUALIANZA)
for check_id in [322, 323]:
    if check_id in inv_by_id:
        inv = inv_by_id[check_id]
        if not inv.get('pdfFile') and 'QUALIANZA' in (inv.get('supplier','') or '').upper():
            src = r'C:\Users\Administrador\Desktop\发票\4月\QUALIANZA_2206659603_2026-04-20.pdf'
            dst = 'QUALIANZA_2206659603.pdf'
            if os.path.exists(src) and not os.path.exists(os.path.join(PDFS_DIR, dst)):
                shutil.copy2(src, os.path.join(PDFS_DIR, dst))
                copied += 1
            inv['pdfFile'] = BASE_URL + dst
            updated += 1
            print(f"[OK] QUALIANZA_2206659603.pdf -> id={check_id} num={inv.get('num','')}")
            break

# Update version
data['version'] = '2026-04-27-v4'

# Write back
new_json = json.dumps(data, ensure_ascii=False, indent=2)
new_content = f"// Generated 2026-04-27 18:00\nvar SEED_DATA = {new_json};"
with open(DATA_JS, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\nCopied: {copied} | Updated: {updated}")
print("data.js updated!")

# Summary: count invoices with/without pdfFile
with_pdf = sum(1 for inv in invoices if inv.get('pdfFile'))
without_pdf = sum(1 for inv in invoices if not inv.get('pdfFile'))
print(f"\nInvoices WITH PDF link: {with_pdf}")
print(f"Invoices WITHOUT PDF link: {without_pdf}")
