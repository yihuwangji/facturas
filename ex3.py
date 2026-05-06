from pypdf import PdfReader
import os

pdf = r'C:\Users\Administrador\Desktop\facturas\invoice_new.pdf'
out_dir = r'C:\Users\Administrador\Desktop\facturas\pdf_pages'
os.makedirs(out_dir, exist_ok=True)

reader = PdfReader(pdf)
print("Pages:", len(reader.pages))

for i, page in enumerate(reader.pages):
    resources = page.get("/Resources", {})
    xobjects = resources.get("/XObject", {})
    for key, obj in xobjects.items():
        subtype = str(obj.get("/Subtype", ""))
        if "/Image" in subtype:
            width = int(obj.get("/Width", 0))
            height = int(obj.get("/Height", 0))
            colorspace = str(obj.get("/ColorSpace", ""))
            filters = str(obj.get("/Filter", ""))
            
            print(f"Page {i+1} {key}: {width}x{height}, CS={colorspace}, Filter={filters}")
            
            # Try to extract
            data = obj.get_data()
            ext = filters if "jpeg" in filters.lower() else ("jpg" if "DCT" in filters else "png")
            out_path = os.path.join(out_dir, f"page{i+1}_{key.replace('/','')}.{ext}")
            with open(out_path, 'wb') as f:
                f.write(data)
            print(f"  -> Saved {len(data)} bytes to {out_path}")

print("Done")