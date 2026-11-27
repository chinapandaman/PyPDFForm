# -*- coding: utf-8 -*-


from PyPDFForm import PdfWrapper


def test_generate_coordinate_grid_margin_50(template_stream, expect_pdf):
    obj = PdfWrapper(template_stream).generate_coordinate_grid((1, 0, 1), margin=50)

    expect_pdf(obj.read())
