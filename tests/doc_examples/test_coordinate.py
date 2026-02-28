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


def test_field_coordinates_dimensions(static_pdfs):
    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))

    assert isinstance(form.widgets["test"].x, float)
    assert isinstance(form.widgets["test"].y, float)
    assert isinstance(form.widgets["test"].width, float)
    assert isinstance(form.widgets["test"].height, float)


def test_change_field_coordinates_dimensions(pdf_samples, static_pdfs, request):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_change_field_coordinates_dimensions.pdf"
    )

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))

    form.widgets["test"].x = (form.widgets["test"].x or 0) - 5
    form.widgets["test"].y = (form.widgets["test"].y or 0) - 5
    form.widgets["test"].width = (form.widgets["test"].width or 0) + 10
    form.widgets["test"].height = (form.widgets["test"].height or 0) + 10

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected
