# -*- coding: utf-8 -*-

import os

from PyPDFForm import BlankPage, Fields, PdfWrapper, RawElements


def test_index_snippets(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_index_snippets.pdf")

    pdf = PdfWrapper(BlankPage())

    pdf.draw(
        [
            RawElements.RawText("My Textfield:", 1, 100, 600),
            RawElements.RawText("My Checkbox:", 1, 100, 550),
        ]
    )
    pdf.bulk_create_fields(
        [
            Fields.TextField("my_textfield", 1, 180, 596, height=16),
            Fields.CheckBoxField("my_checkbox", 1, 180, 546, size=16),
        ]
    )

    assert pdf.schema["properties"]["my_textfield"]["type"] == "string"
    assert pdf.schema["properties"]["my_checkbox"]["type"] == "boolean"

    pdf.widgets["my_textfield"].font_color = (1, 0, 0)
    pdf.widgets["my_textfield"].alignment = 1

    pdf.fill({"my_textfield": "this is a text field", "my_checkbox": True})

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected
