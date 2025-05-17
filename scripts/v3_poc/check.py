from typing import cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject,
                           NameObject)

pdf = PdfReader("pdf_samples/widget/create_checkbox_complex.pdf")
out = PdfWriter()

out.append(pdf)

for page in out.pages:
    for annot in page.get("/Annots", []):
        annot = cast(DictionaryObject, annot.get_object())
        if annot["/T"] != "foo":
            continue

        # size
        rect = annot["/Rect"]
        center_x = (rect[0] + rect[2]) / 2
        center_y = (rect[1] + rect[3]) / 2
        size = 200
        new_rect = [
            FloatObject(center_x - size / 2),
            FloatObject(center_y - size / 2),
            FloatObject(center_x + size / 2),
            FloatObject(center_y + size / 2),
        ]
        annot[NameObject("/Rect")] = ArrayObject(new_rect)


with open("temp/output.pdf", "wb+") as f:
    out.write(f)
