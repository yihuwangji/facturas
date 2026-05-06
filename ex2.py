from pypdf import PdfReader

pdf = r'C:\Users\Administrador\Desktop\facturas\invoice_new.pdf'
reader = PdfReader(pdf)
print("Pages:", len(reader.pages))
print("Metadata:", reader.metadata)

# Check for images in each page
for i, page in enumerate(reader.pages):
    resources = page.get("/Resources", {})
    xobjects = resources.get("/XObject", {})
    img_count = 0
    for key, obj in xobjects.items():
        subtype = obj.get("/Subtype")
        if subtype and str(subtype) == "/Image":
            img_count += 1
            width = obj.get("/Width", "?")
            height = obj.get("/Height", "?")
            print(f"Page {i+1}: Image {key} {width}x{height}")
    if img_count == 0:
        print(f"Page {i+1}: No images found, text length: {len(page.extract_text() or '')}")

# Try raw byte scan for text
with open(pdf, 'rb') as f:
    raw = f.read()

# Look for text streams
import re
# Find BT...ET blocks (text)
bt_blocks = re.findall(b'BT(.*?)ET', raw, re.DOTALL)
print(f"\nText blocks found: {len(bt_blocks)}")
for j, block in enumerate(bt_blocks[:5]):
    print(f"\nBlock {j+1} ({len(block)} bytes):")
    print(block[:500])