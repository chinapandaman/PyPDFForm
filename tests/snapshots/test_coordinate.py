# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_generate_coordinate_grid_margin_50(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "test_generate_coordinate_grid_margin_50.pdf"
    )
    obj = PdfWrapper(template_stream).generate_coordinate_grid((1, 0, 1), margin=50)

    expect_pdf(obj.read(), expected_path)
