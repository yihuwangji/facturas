import re, json, shutil, datetime

data_path = r'C:\Users\Administrador\Desktop\facturas\data.js'
backup_path = r'C:\Users\Administrador\Desktop\facturas\backups\data_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M') + '.js'

with open(data_path, 'r', encoding='utf-8') as f:
    content = f.read()

shutil.copy(data_path, backup_path)

match = re.search(r'var SEED_DATA = (\{.*?\n\});', content, re.DOTALL)
data = json.loads(match.group(1))

print('Before:', len(data['invoices']), 'invoices, nextId:', data['nextId'])

# Add GLUCK & SWEET to suppliers if not exists
suppliers = data.get('suppliers', [])
gluck_nif = 'ES802354413'
existing = [s for s in suppliers if 'GLUCK' in s.get('name','').upper() or s.get('nif') == gluck_nif]
if not existing:
    suppliers.append({
        'name': 'GLUCK & SWEET, S.L.U.',
        'nif': gluck_nif,
        'rate': 10
    })
    print('Added GLUCK & SWEET to suppliers')
else:
    print('GLUCK & SWEET already in suppliers')

new_invoice = {
    'id': data['nextId'],
    'type': 'expense',
    'num': '1102722853',
    'date': '2026-04-30',
    'due': '2026-05-30',
    'supplier': 'GLUCK & SWEET, S.L.U.',
    'nif': gluck_nif,
    'client': 'EUROFAMILIA HORTA SUD, S.L.',
    'cif': 'B98639255',
    'desc': 'FANTASIA MIX BR BOL-1KG VL x12 + HAPPY MIX B-1Kg VL x12',
    'base': 81.54,
    'rate': 10,
    'iva': 8.15,
    'total': 89.69,
    'payMethod': 'pending',
    'status': 'pending',
    'notes': 'Pedido 800662673, Ref 204_514, PAGADO'
}

data['invoices'].append(new_invoice)
data['nextId'] += 1

old_version = data['version']
parts = old_version.rsplit('-v', 1)
data['version'] = parts[0] + '-v' + str(int(parts[1]) + 1)
print('New version:', data['version'])
print('After:', len(data['invoices']), 'invoices, nextId:', data['nextId'])

new_content = 'var SEED_DATA = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';'
with open(data_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

try:
    json.loads(re.search(r'var SEED_DATA = (\{.*?\n\});', open(data_path, 'r', encoding='utf-8').read(), re.DOTALL).group(1))
    print('JSON valid')
except Exception as e:
    print('JSON ERROR:', e)
    shutil.copy(backup_path, data_path)
    print('Restored from backup')