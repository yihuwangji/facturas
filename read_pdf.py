import PyPDF2, sys
path = r'C:\Users\Administrador\.qclaw\media\inbound\FacturaVenta_FVV26010340---7c0af5f0-3a64-4493-8767-403014f0b9fc.pdf'
try:
    with open(path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
    print(text[:3000])
except Exception as e:
    print(f'Error: {e}')
