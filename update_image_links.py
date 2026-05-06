import json, re, shutil
from pathlib import Path

DATA_JS = r'C:\Users\Administrador\Desktop\facturas\data.js'
IMG_DIR = r'C:\Users\Administrador\Desktop\发票\4月'
PDFS_DIR = r'C:\Users\Administrador\Desktop\facturas\pdfs'

# Map invoice numbers to image files
img_map = {
    '2600002326': 'SUPER_RAYO_2600002326_894.47EUR.jpg',
    '20260000953': 'YOUCHENG_20260000953_124.27EUR.jpg',
    '20260000554': 'YOUCHENG_20260000554_27.25EUR.jpg',
    '9205104': 'PRINCESALISIMO_9205104_2222.59EUR.jpg',
    '0321213401': 'FritRavich_0321213401_2026-04-22.jpg',
    '0321319404': 'FritRavich_0321319404_2026-04-22.jpg',
    '26042665': 'JOYVI_26042665_2026-04-23.jpg',
    'E235-60830892': 'MEDIAMARKT_E235-60830892_2026-04-23.jpg'
}

with open(DATA_JS, 'r', encoding='utf-8') as f:
    content = f.read()
m = re.search(r'var SEED_DATA\s*=\s*(\{.*\});', content, re.DOTALL)
data = json.loads(m.group(1))

updated = 0
for inv in data['invoices']:
    num = str(inv.get('num', '')) or str(inv.get('number', ''))
    if num in img_map:
        img_file = img_map[num]
        src = Path(IMG_DIR) / img_file
        dst = Path(PDFS_DIR) / img_file
        
        # Copy image to pdfs folder
        if src.exists():
            shutil.copy2(src, dst)
            print(f'Copied: {img_file}')
        
        # Update pdfFile field
        inv['pdfFile'] = f'pdfs/{img_file}'
        updated += 1
        print(f'Updated id={inv["id"]} num={num} -> pdfs/{img_file}')

# Write back
new_json = json.dumps(data, ensure_ascii=False, indent=2)
new_content = f"// Generated 2026-04-27 18:15\nvar SEED_DATA = {new_json};"
with open(DATA_JS, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'\nTotal updated: {updated} invoices')
print('data.js saved!')
