import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\Administrador\Desktop\facturas\data.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('var SEED_DATA = ', '').rstrip().rstrip(';')
data = json.loads(content)

# Show last 2 invoices
for inv in data['invoices'][-2:]:
    print(f"id={inv['id']} num={inv.get('num','')} total={inv.get('total', inv.get('bankAmt', 0))}")

print(f"nextId={data['nextId']} version={data['version']}")
