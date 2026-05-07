[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$p = "C:\Users\Administrador\Desktop\facturas\inv356.pdf"
$printer = "HP LaserJet MFP M139-M142 PCLm-S"
if (Test-Path $p) {
    Write-Host "File found"
    Start-Process -FilePath $p -Verb PrintTo -ArgumentList $printer -WindowStyle Minimized
    Write-Host "Print job sent"
} else {
    Write-Host "File NOT found"
}
