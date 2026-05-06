$lines = Get-Content 'C:\Users\Administrador\Desktop\facturas\data.js'
$idx = 0
foreach ($line in $lines) {
  if ($line -match '"id": 356') {
    Write-Host "Found at line: $($idx + 1)"
    break
  }
  $idx++
}