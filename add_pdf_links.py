import json, re, os, shutil, sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

DATA_JS = r'C:\Users\Administrador\Desktop\facturas\data.js'
PDFS_DIR = r'C:\Users\Administrador\Desktop\facturas\pdfs'
BASE_URL = 'https://yihuwangji.github.io/facturas/pdfs/'

# Read data.js
with open(DATA_JS, 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'var SEED_DATA\s*=\s*(\{.*\});', content, re.DOTALL)
data = json.loads(match.group(1))
invoices = data['invoices']

# Build maps
inv_by_id = {inv['id']: inv for inv in invoices}
inv_by_num = {}
for inv in invoices:
    if inv.get('num'):
        inv_by_num[inv['num'].strip()] = inv

# Define all PDF-to-invoice mappings
# Format: (source_pdf_path, target_filename, invoice_id)
pdf_mappings = []

# --- MATCHED BY INVOICE NUMBER ---
# 3月 folder
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\3月\2026-03-26_Caravan-Parfum_FVV26006242_542.08EUR.pdf', 'CARAVAN_FVV26006242.pdf', 1))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\3月\2026-03-30_CocaCola_2718375273_4178.35EUR.pdf', 'COCA-COLA_2718375273.pdf', 3))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\3月\2026-03-31_CocaCola_2718425146_FANTA环保费.pdf', 'COCA-COLA_2718425146.pdf', 4))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\3月\2026-03-31_CocaCola_2718425149_PET饮料.pdf', 'COCA-COLA_2718425149.pdf', 5))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\3月\Factura_FVA2604156_.pdf', 'FVA2604156.pdf', None))  # Need to find this invoice
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\3月\Fra_2026_2601653_46264.pdf', 'HERSIGRIM_2601653.pdf', 2))  # id=2 num starts with Fra_2026_2601653

# 4月 folder - matched by number
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\2026-04-01_BEMALU_23Z-324074_杀虫剂.pdf', 'BEMALU_23Z-324074.pdf', 8))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\2026-04-03_LogiTrade_Y26002069_2602.30EUR.pdf', 'LOGITRADE_Y26002069.pdf', 9))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\Coca-Cola_2719520669_426.68EUR.pdf', 'COCA-COLA_2719520669.pdf', 11))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\GOYVAL_EE26147_VINAGRES醋.pdf', 'GOYVAL_EE26147.pdf', 17))

# 4月 folder - PRINCESALISIMO older invoices (9205028, 9205030, 9205033, 9205214)
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\F920502810080_PRINCESALISIMO.pdf', 'PRINCESALISIMO_9205028.pdf', 12))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\F9205030100190_PRINCESALISIMO水.pdf', 'PRINCESALISIMO_9205030.pdf', 13))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\F920503310057_PRINCESALISIMO咖啡零食.pdf', 'PRINCESALISIMO_9205033.pdf', 14))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\F9205214100104_PRINCESALISIMO退货.pdf', 'PRINCESALISIMO_9205214.pdf', 15))

# 4月 folder - GLUCK & SWEET
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\1_76369_2026_04_GLUCK_SWEET糖.pdf', 'GLUCK_SWEET_1_76369.pdf', 16))

# 4月 folder - Servigas (invoice num: 20260228-20260331)
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\2026-04-07_Servigas_Electricidad_20260228-20260331.pdf', 'SERVIGAS_20260228-20260331.pdf', 6))

# 4月 folder - Telecom Calderona (num: FIBRA-300_2940)
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\2026-04-10_Telecom-Calderona_FIBRA-300_2940.pdf', 'TELECOM_FIBRA-300_2940.pdf', 10))

# 4月 folder - MARBUENO
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\MARBUENO_1-404_2026-04-23.pdf', 'MARBUENO_1-404.pdf', None))  # Need to find
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\MARBUENO_PROFORMA_727-1_2026-04-10.pdf', 'MARBUENO_PROFORMA_727-1.pdf', None))  # Proforma, skip?

# 4月 folder - Euro Familia (income invoice)
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\Factura_EURO_FAMILIA_HORTA_SUD.pdf', 'EUROFAMILIA_income.pdf', 7))

# 4月 folder - PRINCESALISIMO 9205397-9205402 (newer batch from 2026-04-20)
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205397_2026-04-20.pdf', 'PRINCESALISIMO_9205397.pdf', None))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205398_2026-04-20.pdf', 'PRINCESALISIMO_9205398.pdf', None))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205399_2026-04-20.pdf', 'PRINCESALISIMO_9205399.pdf', None))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205400_2026-04-20.pdf', 'PRINCESALISIMO_9205400.pdf', None))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205401_2026-04-20.pdf', 'PRINCESALISIMO_9205401.pdf', None))
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\PRINCESALISIMO_9205402_2026-04-20.pdf', 'PRINCESALISIMO_9205402.pdf', None))

# 4月 folder - QUALIANZA
pdf_mappings.append((r'C:\Users\Administrador\Desktop\发票\4月\QUALIANZA_2206659603_2026-04-20.pdf', 'QUALIANZA_2206659603.pdf', None))

# Already in pdfs/ folder (skip, they already have links)
# QUALIANZA_2206659604.pdf -> id=320 (already has link)
# PRINCESALISIMO 9205809-9205816 -> already have links

# Now try to find invoice IDs for the None entries
# Search by invoice num
for i, (src, dst, inv_id) in enumerate(pdf_mappings):
    if inv_id is None:
        # Extract potential invoice numbers from destination filename
        nums = re.findall(r'(\d{4,})', dst.replace('.pdf', ''))
        for num in nums:
            if num in inv_by_num:
                pdf_mappings[i] = (src, dst, inv_by_num[num]['id'])
                break

# Print what we found
print("=== PDF Mappings ===")
copied = 0
updated = 0
skipped = 0

for src, dst, inv_id in pdf_mappings:
    if inv_id is None:
        print(f"  [SKIP - no invoice match] {dst}")
        skipped += 1
        continue
    
    inv = inv_by_id[inv_id]
    if inv.get('pdfFile'):
        print(f"  [SKIP - already has link] {dst} -> id={inv_id}")
        skipped += 1
        continue
    
    # Copy PDF to pdfs/ directory
    if not os.path.exists(src):
        print(f"  [SKIP - source not found] {src}")
        skipped += 1
        continue
    
    target_path = os.path.join(PDFS_DIR, dst)
    if not os.path.exists(target_path):
        shutil.copy2(src, target_path)
        copied += 1
    
    # Update invoice data
    inv['pdfFile'] = BASE_URL + dst
    updated += 1
    print(f"  [OK] {dst} -> id={inv_id} num={inv.get('num','')}")

print()
print(f"Copied: {copied} | Updated: {updated} | Skipped: {skipped}")

# Also find additional invoices without PDFs that we don't have files for
# (just informational)
print()
print("=== Invoices still without PDF files ===")
no_pdf = [inv for inv in invoices if not inv.get('pdfFile') and inv.get('num')]
for inv in no_pdf:
    s = inv.get('supplier', inv.get('client', ''))
    print(f"  id={inv['id']} num={inv['num']} supplier={s} date={inv.get('date','')}")

# Update version
data['version'] = '2026-04-27-v4'

# Write back data.js
new_json = json.dumps(data, ensure_ascii=False, indent=2)
new_content = f"// Generated 2026-04-27 18:00\nvar SEED_DATA = {new_json};"
with open(DATA_JS, 'w', encoding='utf-8') as f:
    f.write(new_content)

print()
print("data.js updated successfully!")
