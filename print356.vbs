Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell -ExecutionPolicy Bypass -Command ""Start-Process -FilePath 'C:\Users\Administrador\Desktop\发票\4月\26001892-EURO-BUSINESS-7-1905.59.pdf' -Verb PrintTo -ArgumentList '\"HP LaserJet MFP M139-M142 PCLm-S\"' -WindowStyle Minimized""", 0, True
WScript.Echo "Print command sent"
