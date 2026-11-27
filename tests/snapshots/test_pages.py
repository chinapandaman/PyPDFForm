# -*- coding: utf-8 -*-


from PyPDFForm import PdfWrapper


def test_pages_preserve_font(template_stream, sample_font_stream, expect_pdf):
    obj = PdfWrapper(template_stream)
    obj.register_font("new_font", sample_font_stream)
    obj.widgets["test_2"].font = "new_font"

    expect_pdf(obj.pages[1].read())


def test_sejda_pages_1(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)

    expect_pdf(obj.pages[0].read())


def test_sejda_pages_2(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)

    expect_pdf(obj.pages[1].read())


def test_radio_pages_1(template_with_radiobutton_stream, expect_pdf):
    obj = PdfWrapper(template_with_radiobutton_stream)

    expect_pdf(obj.pages[0].read())


def test_radio_pages_2(template_with_radiobutton_stream, expect_pdf):
    obj = PdfWrapper(template_with_radiobutton_stream)

    expect_pdf(obj.pages[1].read())


def test_radio_pages_3(template_with_radiobutton_stream, expect_pdf):
    obj = PdfWrapper(template_with_radiobutton_stream)

    expect_pdf(obj.pages[2].read())
