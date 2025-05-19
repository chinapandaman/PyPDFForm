# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_set_text_field_font_size(pdf_samples, template_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_text_field_font_size.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.TRIGGER_WIDGET_HOOKS = True
        obj.widgets["test"].font_size = 30

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
