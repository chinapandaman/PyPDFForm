# -*- coding: utf-8 -*-


from PyPDFForm import BlankPage, PdfWrapper


def test_blank_page(expect_pdf):
    obj = PdfWrapper(BlankPage() * 1)

    expect_pdf(obj.read(), timestamped=True)


def test_blank_page_custom_size_multiply(expect_pdf):
    obj = PdfWrapper(BlankPage(595.35, 841.995) * 3)

    expect_pdf(obj.read(), timestamped=True)
