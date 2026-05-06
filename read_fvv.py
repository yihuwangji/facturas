import fitz, sys
sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open(r'C:\Users\Administrador\.qclaw\media\inbound\FacturaVenta_FVV26010340---7c0af5f0-3a64-4493-8767-403014f0b9fc.pdf')
with open(r'C:\Users\Administrador\Desktop\facturas\fvv_text.txt', 'w', encoding='utf-8') as out:
    for p in doc:
        out.write(p.get_text())
print('done')
