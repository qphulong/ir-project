import sys
import os
import json

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from backend.D2D import D2D

docx_path = "resources/WilliamShakespeare.docx"
pdf_path = "resources/WilliamShakespeare.pdf"
d2d = D2D()

docx_json = d2d.convert_to_json(docx_path)
pdf_json = d2d.convert_to_json(pdf_path)

d2d.save_to_disk("docx.bin", docx_json)
d2d.save_to_disk("pdf.bin", pdf_json)

docx_json = d2d.load_from_disk("docx.bin")
pdf_json = d2d.load_from_disk("pdf.bin")

with open("docx2.json", "w") as f:
    f.write(docx_json)
with open("pdf2.json", "w") as f:
    f.write(pdf_json)