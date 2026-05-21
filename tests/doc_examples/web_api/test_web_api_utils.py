# -*- coding: utf-8 -*-

import json
import os

import pytest
from fastapi.testclient import TestClient

from PyPDFForm import PdfWrapper
from PyPDFForm.api import app

client = TestClient(app)


@pytest.mark.posix_only
@pytest.mark.web_api_test
def test_blank_page(pdf_samples):
    expected_path = os.path.join(pdf_samples, "docs", "test_blank_page.pdf")

    response = client.post("/create/blank")

    assert response.status_code == 200

    with open(expected_path, "rb") as f:
        expected = f.read()

        assert len(expected) == len(response.content)


@pytest.mark.posix_only
@pytest.mark.web_api_test
def test_blank_page_custom_dimensions(pdf_samples):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_blank_page_custom_dimensions.pdf"
    )

    response = client.post("/create/blank", json={"width": 595.35, "height": 841.995})

    assert response.status_code == 200

    with open(expected_path, "rb") as f:
        expected = f.read()

        assert len(expected) == len(response.content)


@pytest.mark.posix_only
@pytest.mark.web_api_test
def test_blank_page_multiply(pdf_samples):
    expected_path = os.path.join(pdf_samples, "docs", "test_blank_page_multiply.pdf")

    response = client.post("/create/blank", json={"count": 3})

    assert response.status_code == 200

    with open(expected_path, "rb") as f:
        expected = f.read()

        assert len(expected) == len(response.content)


@pytest.mark.web_api_test
def test_extract_pages(static_pdfs, pdf_samples, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_extract_pages.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")
    path = os.path.join(static_pdfs, "sample_template.pdf")

    with open(path, "rb") as f:
        extract_result = client.post(
            "/create/extract",
            data={"start": 1, "end": 1},
            files={
                "pdf": ("sample_template.pdf", f, "application/pdf"),
            },
        )

    with open(output_path, "wb") as f:
        f.write(extract_result.content)

    # TODO: fix below with web api calls
    with open(os.path.join(json_samples, "test_extract_pages.json"), "r") as f:
        fill_result = PdfWrapper(output_path).fill(json.load(f))

    with open(expected_path, "rb") as f:
        expected = f.read()
        actual = fill_result.read()

        assert len(expected) == len(actual)
        assert expected == actual
