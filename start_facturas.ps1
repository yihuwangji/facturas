$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process -FilePath node -ArgumentList @('server.js') -WorkingDirectory $root -WindowStyle Minimized
Start-Sleep -Seconds 2
Start-Process 'http://localhost:8765/'
