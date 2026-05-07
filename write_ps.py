import os

pdf_path = r'C:\Users\Administrador\Desktop\发票\4月\26001892-EURO-BUSINESS-7-1905.59.pdf'
printer = 'HP LaserJet MFP M139-M142 PCLm-S'

# Escape single quotes for PowerShell
pdf_ps = pdf_path.replace("'", "''")
printer_ps = printer.replace("'", "''")

script = f"""[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
if (Test-Path '{pdf_ps}'):
    Write-Host 'File found: {pdf_ps}'
    Start-Process -FilePath '{pdf_ps}' -Verb PrintTo -ArgumentList '"{printer_ps}"' -WindowStyle Minimized
    Write-Host 'Print job sent'
else:
    Write-Host 'File NOT found'
"""

out_path = r'C:\Users\Administrador\Desktop\facturas\print356.ps1'
with open(out_path, 'w', encoding='utf-8-sig') as f:
    f.write(script)
print(f'Script written: {out_path}')
print(f'PDF path: {pdf_path}')
print(f'Printer: {printer}')
print(f'Exists: {{}}'.format(os.path.exists(pdf_path)))
