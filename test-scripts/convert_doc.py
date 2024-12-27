import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from backend.D2D import D2D

docx_path = "resources/WilliamShakespeare.docx"
pdf_path = "resources/WilliamShakespeare.pdf"
d2d = D2D()

docx_data = d2d.convert_to_dict(docx_path)
pdf_data = d2d.convert_to_dict(pdf_path)

key = list(docx_data["content"].keys())[0]
print(docx_data["content"][key]["embedding"].__class__)
key = list(pdf_data["content"].keys())[0]
print(docx_data["content"][key]["embedding"].__class__)

d2d.save_to_disk("docx.json", docx_data)
d2d.save_to_disk("pdf.json", pdf_data)

docx_data = d2d.load_from_disk("docx.json")
pdf_data = d2d.load_from_disk("pdf.json")

key = list(docx_data["content"].keys())[0]
print(docx_data["content"][key]["embedding"].__class__)
key = list(pdf_data["content"].keys())[0]
print(docx_data["content"][key]["embedding"].__class__)

d2d.save_to_disk("docx2.json", docx_data)
d2d.save_to_disk("pdf2.json", pdf_data)
