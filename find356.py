with open(r'C:\Users\Administrador\Desktop\facturas\data.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if '"id": 356' in l:
        for j in range(max(0, i - 3), min(len(lines), i + 30)):
            print(j + 1, lines[j], end='')
        break