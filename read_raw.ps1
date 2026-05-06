$bytes = [System.IO.File]::ReadAllBytes("C:\Users\Administrador\.qclaw\media\inbound\扫描文件_20260504_161043---e9666115-f35f-46f1-ade7-ee881d5d564d.pdf")
$text = [System.Text.Encoding]::UTF8.GetString($bytes)
$text | Out-File -FilePath "C:\Users\Administrador\Desktop\facturas\pdf_raw.txt" -Encoding UTF8
"Done, length: $($text.Length)" | Out-Host