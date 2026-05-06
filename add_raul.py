import re, json, os, shutil, datetime

# Load data.js
data_path = r'C:\Users\Administrador\Desktop\facturas\data.js'
backup_path = r'C:\Users\Administrador\Desktop\facturas\backups\data_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M') + '.js'

with open(data_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
shutil.copy(data_path, backup_path)
print('Backup:', backup_path)

# Parse
match = re.search(r'var SEED_DATA = (\{.*?\n\});', content, re.DOTALL)
data = json.loads(match.group(1))

print('Before:', len(data['invoices']), 'invoices, nextId:', data['nextId'])

# Add RAUL BERMELL to suppliers if not exists
suppliers = data.get('suppliers', [])
raul_nif = '52685200-C'
existing = [s for s in suppliers if s.get('nif') == raul_nif]
if not existing:
    suppliers.append({
        'name': 'RAUL BERMELL ROSELLO',
        'nif': raul_nif,
        'rate': 10
    })
    print('Added RAUL BERMELL to suppliers')
else:
    print('RAUL BERMELL already in suppliers')

# New invoices
new_invoices = [
    {
        'id': 347,
        'type': 'expense',
        'num': '7584',
        'date': '2026-05-03',
        'due': '2026-05-04',
        'supplier': 'RAUL BERMELL ROSELLO',
        'nif': raul_nif,
        'client': 'EUROFAMILIA HORTA SUD, S.L.',
        'cif': 'B98639255',
        'desc': 'ACEITUNA COCTEL BOT 5 KG x 70',
        'base': 840.00,
        'rate': 10,
        'iva': 84.00,
        'total': 924.00,
        'payMethod': 'pending',
        'status': 'pending',
        'notes': ''
    },
    {
        'id': 348,
        'type': 'expense',
        'num': '7585',
        'date': '2026-05-03',
        'due': '2026-05-06',
        'supplier': 'RAUL BERMELL ROSELLO',
        'nif': raul_nif,
        'client': 'EUROFAMILIA HORTA SUD, S.L.',
        'cif': 'B98639255',
        'desc': 'ACEITUNA COCTEL CUBO x 45',
        'base': 877.50,
        'rate': 10,
        'iva': 87.75,
        'total': 965.25,
        'payMethod': 'pending',
        'status': 'pending',
        'notes': ''
    },
    {
        'id': 349,
        'type': 'expense',
        'num': '7586',
        'date': '2026-05-05',
        'due': '2026-05-06',
        'supplier': 'RAUL BERMELL ROSELLO',
        'nif': raul_nif,
        'client': 'EUROFAMILIA HORTA SUD, S.L.',
        'cif': 'B98639255',
        'desc': 'ACEITUNA COCTEL CUBO x 27',
        'base': 526.50,
        'rate': 10,
        'iva': 52.65,
        'total': 579.15,
        'payMethod': 'pending',
        'status': 'pending',
        'notes': ''
    }
]

data['invoices'].extend(new_invoices)
data['nextId'] = 350

# Bump version
old_version = data['version']
parts = old_version.rsplit('-v', 1)
if len(parts) == 2:
    data['version'] = parts[0] + '-v' + str(int(parts[1]) + 1)
else:
    data['version'] = old_version + '-v1'

print('New version:', data['version'])
print('After:', len(data['invoices']), 'invoices, nextId:', data['nextId'])

# Save
new_content = 'var SEED_DATA = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';'
with open(data_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Saved to', data_path)

# Verify JSON
try:
    json.loads(re.search(r'var SEED_DATA = (\{.*?\n\});', open(data_path, 'r', encoding='utf-8').read(), re.DOTALL).group(1))
    print('JSON valid')
except Exception as e:
    print('JSON ERROR:', e)
    shutil.copy(backup_path, data_path)
    print('Restored from backup')