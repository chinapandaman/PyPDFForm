# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_register_font(static_pdfs, sample_font_stream):
    obj = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    obj.register_font("new_font_name", sample_font_stream)

    assert "new_font_name" in obj.fonts
