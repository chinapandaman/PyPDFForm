from typing import cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (DictionaryObject, NameObject, NumberObject,
                           TextStringObject)

pdf = PdfReader("pdf_samples/sample_template_with_complex_fonts.pdf")
out = PdfWriter()

out.append(pdf)

for page in out.pages:
    for annot in page.get("/Annots", []):
        annot = cast(DictionaryObject, annot.get_object())
        da = annot["/DA"].split(" ")
        da[1] = "20"  # font_size
        da = da[:3] + ["0", "1", "0", "rg"]  # font_color
        annot[NameObject("/DA")] = TextStringObject(" ".join(da))
        annot[NameObject("/MaxLen")] = NumberObject(2)  # max_length
        annot[NameObject("/Ff")] = NumberObject(annot["/Ff"] | 1 << 24)  # comb

with open("temp/output.pdf", "wb+") as f:
    out.write(f)
