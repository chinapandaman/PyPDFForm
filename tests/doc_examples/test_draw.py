# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_draw_text(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_text.pdf")

    pdf = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf")
    ).draw_text(
        text="random text",
        page_number=1,
        x=300,
        y=225,
        font="Helvetica",  # optional
        font_size=12,  # optional
        font_color=(1, 0, 0),  # optional
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_draw_image(static_pdfs, image_samples, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_image.pdf")

    pdf = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf")
    ).draw_image(
        image=os.path.join(image_samples, "sample_image.jpg"),
        page_number=1,
        x=100,
        y=100,
        width=400,
        height=225,
        rotation=0,  # optional
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected
