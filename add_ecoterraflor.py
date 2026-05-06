import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\Administrador\Desktop\facturas\data.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('var SEED_DATA = ', '').rstrip().rstrip(';')
data = json.loads(content)

new_inv = {
    "id": 355,
    "type": "expense",
    "num": "26/1116",
    "date": "2026-04-30",
    "due": "2026-06-30",
    "supplier": "ECOTERRAFLOR, S.L.U.",
    "nif": "B-47416755",
    "client": "EUROFAMILIA HORTA SUR S.L.",
    "cif": "B98639255",
    "desc": "SACO ECOTERRAFLOR 50L - 576 uds (DTO.COM. -52 uds)",
    "base": 1150.18,
    "rate": 10,
    "iva": 115.02,
    "total": 1265.20,
    "payMethod": "transferencia",
    "status": "pending",
    "notes": "Albaran 26/1212 Fecha 27/04/2026, Pedido VN/26-00062, pago 60 dias transferencia, CC ES53 2100 3754 1322 00010779"
}

data['invoices'].append(new_inv)
data['nextId'] = 356

output = 'var SEED_DATA = ' + json.dumps(data, indent=2, ensure_ascii=False) + ';'
with open(r'C:\Users\Administrador\Desktop\facturas\data.js', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"Added invoice id=355. Total invoices: {len(data['invoices'])}. nextId={data['nextId']}")
