# -*- coding: utf-8 -*-

import os

from PyPDFForm import Fields, PdfWrapper, RawElements


def test_register_font_no_form_fields(pdf_samples, sample_font_stream, expect_pdf):
    obj = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
    obj.register_font("new_font", sample_font_stream).bulk_create_fields(
        [Fields.TextField(name="foo", page_number=1, x=100, y=100, font="new_font")]
    )
    obj.draw([RawElements.RawText("foo", 1, 200, 200, font="new_font")])

    expect_pdf(obj.read())
