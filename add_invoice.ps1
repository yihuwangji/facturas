# Read the file
$content = Get-Content 'C:\Users\Administrador\Desktop\facturas\data.js' -Raw

# The new invoice to add (RUSHER SC - HEINEKEN)
$newInvoice = @"
      {
        "id": 358,
        "type": "expense",
        "num": "INV/2026/05/00003",
        "date": "2026-05-05",
        "due": "2026-05-05",
        "supplier": "RUSHER SC",
        "nif": "J75996124",
        "desc": "HEINEKEN 1/3 CRISTAL (63 uds)",
        "base": 811.44,
        "ivaRate": 21,
        "ivaAmt": 170.40,
        "irpfRate": 0,
        "irpfAmt": 0,
        "total": 981.84,
        "payMethod": "paid",
        "bankAmt": 981.84,
        "cashAmt": 0,
        "payDate": "2026-05-06",
        "status": "paid",
        "notes": ""
      }
"@

# Find position to insert - after invoice 357
# We look for the closing of invoices array
$pattern = '(\s+\],\s*\n\s+\"suppliers\":)'

if ($content -match $pattern) {
    $insertPosition = $matches[0].Index
    $newContent = $content.Substring(0, $insertPosition) + "`n" + $newInvoice + "`n    " + $content.Substring($insertPosition)
    $newContent | Set-Content 'C:\Users\Administrador\Desktop\facturas\data.js' -NoNewline
    Write-Host "Invoice added successfully"
} else {
    Write-Host "Pattern not found"
}