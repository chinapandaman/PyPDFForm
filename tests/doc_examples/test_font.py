# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_register_font(static_pdfs, sample_font_stream, font_samples):
    obj = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    obj.register_font("new_font_name", sample_font_stream)

    assert "new_font_name" in obj.fonts

    obj2 = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    with open(
        os.path.join(font_samples, "LiberationSerif-BoldItalic.ttf"), "rb+"
    ) as font_file:
        obj2.register_font("new_font_name_2", font_file)
    assert "new_font_name_2" in obj2.fonts

    obj3 = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    with open(
        os.path.join(font_samples, "LiberationSerif-BoldItalic.ttf"), "rb+"
    ) as font_file:
        obj3.register_font("new_font_name_3", font_file.read())
    assert "new_font_name_3" in obj3.fonts
