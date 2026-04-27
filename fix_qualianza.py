import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

DATA_JS = r'C:\Users\Administrador\Desktop\facturas\data.js'

with open(DATA_JS, 'r', encoding='utf-8') as f:
    content = f.read()
m = re.search(r'var SEED_DATA\s*=\s*(\{.*\});', content, re.DOTALL)
data = json.loads(m.group(1))

# Update QUALIANZA id=322
for inv in data['invoices']:
    if inv['id'] == 322:
        inv['num'] = '2206659603'
        inv['base'] = 2297.28
        inv['ivaRate'] = 21
        inv['ivaAmt'] = 229.73
        inv['total'] = 2527.01
        inv['bankAmt'] = 2527.01
        inv['desc'] = 'PRODUCTOS ALIMENTARIOS'
        inv['payMethod'] = 'recibo'
        print(f"Updated id=322: num={inv['num']} total={inv['total']}")
        break

# Write back
new_json = json.dumps(data, ensure_ascii=False, indent=2)
new_content = f"// Generated 2026-04-27 18:00\nvar SEED_DATA = {new_json};"
with open(DATA_JS, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("data.js updated!")
