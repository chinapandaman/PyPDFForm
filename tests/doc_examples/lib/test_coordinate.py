# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_coordinate_grid_view(static_pdfs, expect_pdf):
    grid_view_pdf = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf")
    ).generate_coordinate_grid(
        color=(1, 0, 0),  # optional
        margin=100,  # optional
    )

    expect_pdf(grid_view_pdf.read())


def test_field_locations_dimensions(static_pdfs):
    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))

    assert form.widgets["test"].page_number == 1
    assert isinstance(form.widgets["test"].x, float)
    assert isinstance(form.widgets["test"].y, float)
    assert isinstance(form.widgets["test"].width, float)
    assert isinstance(form.widgets["test"].height, float)


def test_change_field_coordinates_dimensions(static_pdfs, expect_pdf):
    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))

    form.widgets["test"].x = 68.3365
    form.widgets["test"].y = 657.692
    form.widgets["test"].width = 242.4235
    form.widgets["test"].height = 31.067999999999984

    expect_pdf(form.read())
