# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_coordinate_grid_view(pdf_samples, static_pdfs, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_coordinate_grid_view.pdf")

    grid_view_pdf = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf")
    ).generate_coordinate_grid(
        color=(1, 0, 0), margin=100  # optional
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = grid_view_pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(grid_view_pdf.read()) == len(expected)
        assert grid_view_pdf.read() == expected
