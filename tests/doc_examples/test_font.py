# -*- coding: utf-8 -*-

from PyPDFForm import PdfWrapper


def test_register_font(template_stream, sample_font_stream):
    obj = PdfWrapper(template_stream)
    obj.register_font("new_font_name", sample_font_stream)

    assert "new_font_name" in obj.fonts
