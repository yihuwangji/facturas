import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\Administrador\Desktop\facturas\data.js', 'r', encoding='utf-8') as f:
    c = f.read()
m = re.search(r'var SEED_DATA\s*=\s*(\{.*\});', c, re.DOTALL)
d = json.loads(m.group(1))
for inv in d['invoices']:
    num = inv.get('num', '')
    if 'FVA' in str(num) or '2604156' in str(num):
        print(f"id={inv['id']} num={num} type={inv.get('type','')} supplier={inv.get('supplier','')} client={inv.get('client','')}")
