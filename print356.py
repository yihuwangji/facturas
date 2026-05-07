import subprocess
import sys

pdf_path = r"C:\Users\Administrador\Desktop\发票\4月\26001892-EURO-BUSINESS-7-1905.59.pdf"
printer = "HP LaserJet MFP M139-M142 PCLm-S"

# Try using the Windows print command
try:
    result = subprocess.run(
        ['print', '/D:' + printer, pdf_path],
        capture_output=True,
        text=True,
        timeout=30
    )
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
except FileNotFoundError:
    print("print command not found, trying alternative...")
except Exception as e:
    print(f"Error: {e}")
