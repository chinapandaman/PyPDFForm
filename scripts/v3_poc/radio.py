from typing import cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject,
                           NameObject)

pdf = PdfReader("pdf_samples/sample_template_with_radio_button.pdf")
out = PdfWriter()

out.append(pdf)

for page in out.pages:
    for annot in page.get("/Annots", []):
        annot = cast(DictionaryObject, annot.get_object())
        if "/Parent" in annot and annot["/Parent"]["/T"] != "radio_1":
            continue

        # size
        rect = annot["/Rect"]
        center_x = (rect[0] + rect[2]) / 2
        center_y = (rect[1] + rect[3]) / 2
        size = 40
        new_rect = [
            FloatObject(center_x - size / 2),
            FloatObject(center_y - size / 2),
            FloatObject(center_x + size / 2),
            FloatObject(center_y + size / 2),
        ]
        annot[NameObject("/Rect")] = ArrayObject(new_rect)


with open("temp/output.pdf", "wb+") as f:
    out.write(f)
