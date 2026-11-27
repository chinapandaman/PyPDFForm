# -*- coding: utf-8 -*-

import os

from PyPDFForm import BlankPage, PdfWrapper


def test_blank_page(pdf_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "test_blank_page.pdf")
    obj = PdfWrapper(BlankPage() * 1)

    expect_pdf(obj.read(), expected_path, timestamped=True)


def test_blank_page_custom_size_multiply(pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "test_blank_page_custom_size_multiply.pdf"
    )
    obj = PdfWrapper(BlankPage(595.35, 841.995) * 3)

    expect_pdf(obj.read(), expected_path, timestamped=True)
