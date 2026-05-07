import json, re, sys

with open(r'C:\Users\Administrador\Desktop\facturas\data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JSON from var SEED_DATA = {...}
match = re.search(r'var SEED_DATA\s*=\s*(\{[\s\S]*\});?\s*$', content.strip())
if not match:
    print("No SEED_DATA found")
    sys.exit(1)

data = json.loads(match.group(1))
for inv in data.get('invoices', []):
    if inv.get('id') == 356:
        print(json.dumps(inv, indent=2, ensure_ascii=False))
        break
else:
    print(f"Invoice 356 not found. Total: {len(data.get('invoices',[]))}")