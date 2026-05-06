import json

with open(r'C:\Users\Administrador\Desktop\facturas\data.js', 'r', encoding='utf-8') as f:
    txt = f.read()

start = txt.index('{')
txt = txt[start:].rstrip().rstrip(';').rstrip()
d = json.loads(txt)

print(f"nextId: {d['nextId']}")
print(f"invoice count: {len(d['invoices'])}")
print("Last 5 invoices:")
for inv in d['invoices'][-5:]:
    print(f"  id={inv['id']} num={inv.get('num','')} supplier={inv.get('supplier','')} total={inv.get('total','')}")
