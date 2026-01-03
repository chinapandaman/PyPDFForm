# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_text_field_scripts(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "js", "test_text_field_scripts.pdf")
    with open(expected_path, "rb+") as f:
        pdf = PdfWrapper(template_stream)
        pdf.widgets["test"].on_hovered_over_javascript = (
            'this.getField("test").value = "hoverover";'
        )
        pdf.widgets["test"].on_hovered_off_javascript = (
            'this.getField("test").value = "hoveroff";'
        )
        pdf.widgets["test"].on_mouse_pressed_javascript = (
            'this.getField("test").value = "pressed";'
        )
        pdf.widgets["test"].on_mouse_released_javascript = (
            'this.getField("test").value = "released";'
        )

        pdf.widgets["test_2"].on_focused_javascript = (
            'this.getField("test_2").value = "focused";'
        )
        pdf.widgets["test_2"].off_focused_javascript = (
            'this.getField("test_2").value = "defocused";'
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = pdf.read()

        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected
