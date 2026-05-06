import fitz, sys
sys.stdout.reconfigure(encoding='utf-8')
doc = fitz.open(r'C:\Users\Administrador\.qclaw\media\inbound\61_2---cfdf1965-674c-432b-8bfb-7b476ec53758.pdf')
with open(r'C:\Users\Administrador\Desktop\facturas\pdf2_text.txt', 'w', encoding='utf-8') as out:
    for p in doc:
        out.write(p.get_text())
print('done')