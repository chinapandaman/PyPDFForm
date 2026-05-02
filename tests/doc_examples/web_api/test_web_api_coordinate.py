# -*- coding: utf-8 -*-

import json
import os

import pytest
from fastapi.testclient import TestClient

from PyPDFForm import PdfWrapper
from PyPDFForm.api import app

client = TestClient(app)


@pytest.mark.web_api_test
def test_coordinate_grid_view(pdf_samples, static_pdfs):
    expected_path = os.path.join(pdf_samples, "docs", "test_coordinate_grid_view.pdf")
    path = os.path.join(static_pdfs, "sample_template.pdf")
    with open(path, "rb") as f:
        response = client.post(
            "/create/grid",
            data={
                "red": 1,
                "green": 0,
                "blue": 0,
                "margin": 100,
            },
            files={
                "pdf": ("sample_template.pdf", f, "application/pdf"),
            },
        )

    assert response.status_code == 200

    with open(expected_path, "rb") as f:
        expected = f.read()

        assert len(expected) == len(response.content)
        assert expected == response.content


@pytest.mark.web_api_test
def test_field_page_number_coordinates_dimensions(static_pdfs):
    path = os.path.join(static_pdfs, "sample_template.pdf")
    with open(path, "rb") as f:
        response = client.post(
            "/inspect/location",
            data={"field": "test"},
            files={
                "pdf": ("sample_template.pdf", f, "application/pdf"),
            },
        )

    assert response.status_code == 200

    wrapper = PdfWrapper(path)
    obj = json.loads(response.content)
    assert obj["page_number"] == wrapper.widgets["test"].page_number
    assert obj["x"] == wrapper.widgets["test"].x
    assert obj["y"] == wrapper.widgets["test"].y
    assert obj["width"] == wrapper.widgets["test"].width
    assert obj["height"] == wrapper.widgets["test"].height
