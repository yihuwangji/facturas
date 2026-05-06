import re, json

with open(r'C:\Users\Administrador\Desktop\facturas\data.js', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'var SEED_DATA = (\{.*?\n\});', content, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    print('Version:', data['version'])
    print('nextId:', data['nextId'])
    print('Invoice count:', len(data['invoices']))
    
    # Check suppliers
    suppliers = data.get('suppliers', [])
    raul = [s for s in suppliers if 'RAUL' in s.get('name','').upper() or 'BERMELL' in s.get('name','').upper()]
    print('RAUL BERMELL in suppliers:', raul)
    
    # Check for existing RAUL invoices
    raul_invs = [i for i in data['invoices'] if 'BERMELL' in i.get('supplier','').upper()]
    print('Existing RAUL invoices:', len(raul_invs))
    
    # Last few invoices
    for inv in data['invoices'][-3:]:
        sid = inv['id']
        sdate = inv['date']
        ssupp = inv['supplier']
        stotal = inv.get('total', 0)
        print(f"  id={sid} {sdate} {ssupp} {stotal} EUR")
else:
    print('Could not parse SEED_DATA')