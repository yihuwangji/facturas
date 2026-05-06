import json, re, os
from pathlib import Path

DATA_JS = r'C:\Users\Administrador\Desktop\facturas\data.js'
IMG_DIR = r'C:\Users\Administrador\Desktop\发票\4月'

with open(DATA_JS, 'r', encoding='utf-8') as f:
    content = f.read()
m = re.search(r'var SEED_DATA\s*=\s*(\{.*\});', content, re.DOTALL)
data = json.loads(m.group(1))

# Image files found
img_files = [
    '2026-04-17_SUPERRAYO_2600002326_894.47EUR.jpg',
    '2026-04-18_YOUCHENG_20260000554_27.25EUR.jpg',
    '2026-04-18_YOUCHENG_20260000953_124.27EUR.jpg',
    'FritRavich_0321213401_2026-04-22.jpg',
    'FritRavich_0321319404_2026-04-22.jpg',
    'JOYVI_26042665_2026-04-23.jpg',
    'MEDIAMARKT_E235-60830892_2026-04-23.jpg',
    'PRINCESALISIMO_9205104_2222.59EUR.jpg',
    'SUPER_RAYO_2600002326_894.47EUR.jpg',
    'YOUCHENG_20260000554_27.25EUR.jpg',
    'YOUCHENG_20260000953_124.27EUR.jpg'
]

print("Checking image invoices in system:")
print("="*60)
exists = []
not_exists = []

for img_file in img_files:
    # Extract invoice number
    img_path = Path(IMG_DIR) / img_file
    num = None
    
    # Try to extract number from filename
    if '2600002326' in img_file:
        num = '2600002326'
    elif '20260000554' in img_file:
        num = '20260000554'
    elif '20260000953' in img_file:
        num = '20260000953'
    elif '0321213401' in img_file:
        num = '0321213401'
    elif '0321319404' in img_file:
        num = '0321319404'
    elif '26042665' in img_file:
        num = '26042665'
    elif 'E235-60830892' in img_file:
        num = 'E235-60830892'
    elif '9205104' in img_file:
        num = '9205104'
    
    if num:
        found = [inv for inv in data['invoices'] if str(inv.get('num', '')) == num]
        if found:
            print(f"  ✓ {num} - EXISTS (id={found[0]['id']}, file={img_file})")
            exists.append((num, found[0]['id'], img_file))
        else:
            print(f"  ✗ {num} - NOT FOUND (file={img_file})")
            not_exists.append((num, img_file))
    else:
        print(f"  ? Cannot extract number from {img_file}")

print("\n" + "="*60)
print(f"Already in system: {len(exists)}")
print(f"Need to add: {len(not_exists)}")
if not_exists:
    print("\nInvoices to add:")
    for num, img in not_exists:
        print(f"  - {num} ({img})")
