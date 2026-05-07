import os

pdf_path = r'C:\Users\Administrador\Desktop\发票\4月\26001892-EURO-BUSINESS-7-1905.59.pdf'
printer = 'HP LaserJet MFP M139-M142 PCLm-S'

pdf_ps = pdf_path.replace("'", "''")
printer_ps = printer.replace("'", "''")

script = f"""[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$p = '{pdf_ps}'
Write-Host "Path: $p"
Write-Host "Exists: $(os.path.exists(pdf_path))"
if (Test-Path $p):
    Write-Host "File found"
    Start-Process -FilePath $p -Verb PrintTo -ArgumentList '"{printer_ps}"' -WindowStyle Minimized
    Write-Host "Print job sent"
else:
    Write-Host "File NOT found"
"""

with open(r'C:\Users\Administrador\Desktop\facturas\print356.ps1', 'w', encoding='utf-8-sig') as f:
    f.write(script)
print("OK")
