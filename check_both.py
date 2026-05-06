import subprocess

# Check if id=345 (YOUCHENG) is in the committed version
result = subprocess.run(['git', 'show', 'HEAD:data.js'], capture_output=True, text=True, encoding='utf-8', cwd=r'C:\Users\Administrador\Desktop\facturas')
txt = result.stdout

# Search for YOUCHENG
if 'YOUCHENG' in txt:
    idx = txt.index('YOUCHENG')
    print(f"YOUCHENG found at char {idx}")
    print(f"Context: ...{txt[max(0,idx-100):idx+200]}...")
else:
    print("YOUCHENG NOT found in committed version!")

# Search for id 345
if '"id": 345' in txt or '"id":345' in txt:
    print("\nid=345 found in committed version")
else:
    print("\nid=345 NOT found in committed version!")

# Search for 2026001083
if '2026001083' in txt:
    print("Invoice 2026001083 found in committed version")
else:
    print("Invoice 2026001083 NOT found in committed version!")

# Count invoices roughly
count = txt.count('"id":')
print(f"\nRough id count: {count}")

# Check version line
for line in txt.split('\n'):
    if 'version' in line:
        print(f"Version line: {line.strip()}")
        break
