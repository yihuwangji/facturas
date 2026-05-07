#!/usr/bin/env python3
"""Fix data.js - find and repair broken quote strings"""
import sys, re, json

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\Administrador\Desktop\facturas\data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix known broken strings by finding unclosed quotes in desc/notes fields
# Pattern: "desc": "some text with broken chars,
# The issue is that the original data had multi-byte UTF-8 chars that got truncated,
# leaving an unclosed string like "FANTA环保?,

# Strategy: find all broken patterns and fix them
# Known broken patterns (from the error lines):
fixes = [
    # Line 90 & 101: FANTA环保
    (r'"desc":\s*"FANTA环保\?', '"desc": "FANTA环保瓶"'),
    (r'"notes":\s*"FANTA环保\?', '"notes": "FANTA环保瓶"'),
    # Line 165 & 176: 折叠
    (r'"desc":\s*"折叠\?', '"desc": "折叠桌"'),
    (r'"notes":\s*"折叠\?', '"notes": "折叠桌"'),
    # Line 315 & 326: standalone ?
    (r'"desc":\s*"\?', '"desc": ""'),
    (r'"notes":\s*"\?', '"notes": ""'),
    # Line 365 & 376: 退
    (r'"desc":\s*"退\?', '"desc": "退款"'),
    (r'"notes":\s*"退\?', '"notes": "退款"'),
    # Line 390 & 401, 415 & 426: more standalone ?
    # These are already caught by the "standalone ?" pattern above
    # Line 465 & 476: 打火机气体
    (r'"desc":\s*"打火\?气体"', '"desc": "打火机气体"'),
    (r'"notes":\s*"打火\?气体"', '"notes": "打火机气体"'),
    # Line 490 & 501: 塑料制品圆珠笔
    (r'"desc":\s*"塑料\?圆珠\?', '"desc": "塑料制品圆珠笔"'),
    (r'"notes":\s*"塑料\?圆珠\?', '"notes": "塑料制品圆珠笔"'),
    # Line 540: 小商品批发(713件)
    (r'"desc":\s*"小商品批\?\(713\?', '"desc": "小商品批发(713件)"'),
    # Line 564: 小商品批发713件
    (r'"desc":\s*"小商品批\?713\?', '"desc": "小商品批发713件"'),
    # Line 588: 小商品批发50件
    (r'"desc":\s*"小商品批\?50\?', '"desc": "小商品批发50件"'),
    # Line 695: Bruto line
    (r'"notes":\s*"FACTURA PROFORMA - Entrega 20/04/2026 - Bruto 1633\.04\?-\\tdto 20%% 326\.61\?', '"notes": "FACTURA PROFORMA - Entrega 20/04/2026 - Bruto 1633.04€\\tdto 20%% 326.61€"'),
    # Line 7598: 退单
    (r'"desc":\s*"退单（负数\?', '"desc": "退单(负数)"'),
    # Line 7623: 每日营业额
    (r'"desc":\s*"每日营业\?', '"desc": "每日营业额"'),
    # Line 8165: 888件
    (r'"notes":\s*"TEXTIL SANO 袜子 888\?', '"notes": "TEXTIL SANO 袜子 888件"'),
    # Line 8179 & 8190: 宠物用品
    (r'"desc":\s*"CANZO GLOBAL 靠垫/枕头/宠物\?', '"desc": "CANZO GLOBAL 靠垫/枕头/宠物用品"'),
    (r'"notes":\s*"CANZO GLOBAL 靠垫/枕头/宠物\?425\?', '"notes": "CANZO GLOBAL 靠垫/枕头/宠物用品425件"'),
]

for pattern, replacement in fixes:
    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        print(f"Fixed: {pattern[:50]}... -> {replacement}")
        content = new_content

# Also fix any remaining unclosed quotes with a broader pattern
# Find lines like: "key": "value?,  (missing closing quote before comma)
lines = content.split('\n')
fixed_lines = []
changes = 0
for line in lines:
    # Check for pattern: "desc": "something?  or "notes": "something?
    m = re.match(r'^(\s*"(?:desc|notes)":\s*")([^"]*?)\?(,\s*)$', line)
    if m:
        prefix = m.group(1)
        value = m.group(2)
        suffix = m.group(3)
        # The ? is a broken char - replace with reasonable text and close quote
        fixed = f'{prefix}{value}"{suffix}'
        print(f"Fixed unclosed quote: {line.strip()[:80]} -> {fixed.strip()[:80]}")
        line = fixed
        changes += 1
    fixed_lines.append(line)

if changes:
    content = '\n'.join(fixed_lines)

with open(r'C:\Users\Administrador\Desktop\facturas\data.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal changes: {len(fixes) + changes}")
print("Done!")
