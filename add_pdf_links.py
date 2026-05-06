import re, json, datetime

data_path = r'C:\Users\Administrador\Desktop\facturas\data.js'

with open(data_path, 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'var SEED_DATA = (\{.*?\n\});', content, re.DOTALL)
data = json.loads(match.group(1))

# Add pdfFile to the 3 new invoices
pdf_links = {
    347: 'pdfs/RAUL_BERMELL_7584.jpg',
    348: 'pdfs/RAUL_BERMELL_7585.jpg',
    349: 'pdfs/RAUL_BERMELL_7586.jpg'
}

for inv in data['invoices']:
    if inv['id'] in pdf_links:
        inv['pdfFile'] = pdf_links[inv['id']]
        print(f"Added pdfFile to id={inv['id']}: {inv['pdfFile']}")

print('Saving...')
new_content = 'var SEED_DATA = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';'
with open(data_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Done')

# Verify
match2 = re.search(r'var SEED_DATA = (\{.*?\n\});', open(data_path, 'r', encoding='utf-8').read(), re.DOTALL)
data2 = json.loads(match2.group(1))
for inv in data2['invoices']:
    if inv['id'] in pdf_links:
        print(f"id={inv['id']} pdfFile: {inv.get('pdfFile','MISSING')}")