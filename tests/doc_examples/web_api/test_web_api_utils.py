# -*- coding: utf-8 -*-

import os

import pytest
from fastapi.testclient import TestClient

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
