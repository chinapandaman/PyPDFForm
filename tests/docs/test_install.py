# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_create_pdf_wrapper(template_stream, pdf_samples):
    pdf = PdfWrapper(template_stream)

    assert pdf.read()

    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as template:
        pdf_2 = PdfWrapper(template)

    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as template:
        pdf_3 = PdfWrapper(template.read())

    assert pdf.read() == pdf_2.read()
    assert pdf.read() == pdf_3.read()


def test_create_adobe_mode_wrapper(template_stream):
    pdf = PdfWrapper(template_stream, adobe_mode=True)

    assert getattr(pdf, "adobe_mode")
    assert pdf.read() != PdfWrapper(template_stream).read()


def test_use_full_widget_name(pdf_samples):
    pdf = PdfWrapper(
        os.path.join(pdf_samples, "sample_template_with_full_key.pdf"), use_full_widget_name=True
    )

    assert getattr(pdf, "use_full_widget_name")
    assert "Gain de 2 classes.0" in pdf.widgets
    assert "0" not in pdf.widgets
