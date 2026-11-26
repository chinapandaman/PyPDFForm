# -*- coding: utf-8 -*-

import os

from PyPDFForm import BlankPage, Fields, PdfWrapper, RawElements


def test_index_snippets(pdf_samples, monkeypatch, expect_pdf):
    # Stable ReportLab timestamps prevent variable-length document IDs.
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "946684800")
    expected_path = os.path.join(pdf_samples, "docs", "test_index_snippets.pdf")

    # Create a blank PDF
    pdf = PdfWrapper(BlankPage())
    pdf = PdfWrapper(pdf.read())  # not in docs, to keep artifact consistent with CLI

    # Draw labeling texts
    pdf.draw(
        [
            RawElements.RawText("My Textfield:", 1, 100, 600),
            RawElements.RawText("My Checkbox:", 1, 100, 550),
        ]
    )
    pdf = PdfWrapper(pdf.read())  # not in docs, to keep artifact consistent with CLI

    # Create text and checkbox fields
    pdf.bulk_create_fields(
        [
            Fields.TextField("my_textfield", 1, 180, 596, height=16),
            Fields.CheckBoxField("my_checkbox", 1, 180, 546, size=16),
        ]
    )
    pdf = PdfWrapper(pdf.read())  # not in docs, to keep artifact consistent with CLI

    # Inspect the fields via JSON schema
    assert pdf.schema["properties"]["my_textfield"]["type"] == "string"
    assert pdf.schema["properties"]["my_checkbox"]["type"] == "boolean"

    # Change the field styles
    pdf.widgets["my_textfield"].font_color = (1, 0, 0)
    pdf.widgets["my_textfield"].alignment = 1
    pdf = PdfWrapper(pdf.read())  # not in docs, to keep artifact consistent with CLI

    # Fill the newly created form
    pdf.fill({"my_textfield": "this is a text field", "my_checkbox": True})

    expect_pdf(pdf.read(), expected_path, timestamped=True)

    assert pdf.widgets["my_textfield"].alignment == 1
    assert pdf.data["my_textfield"] == "this is a text field"
    assert pdf.data["my_checkbox"]
