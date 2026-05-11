# -*- coding: utf-8 -*-

import os

import pytest
from fastapi.testclient import TestClient

from PyPDFForm.api import app

client = TestClient(app)


def assert_web_api_error(response, status_code, *expected_messages):
    assert response.status_code == status_code
    detail = response.json()["detail"]
    for message in expected_messages:
        assert message in detail


@pytest.mark.web_api_test
def test_index_redirect_to_docs():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


@pytest.mark.web_api_test
def test_inspect_location_unknown_field(pdf_samples):
    path = os.path.join(pdf_samples, "sample_template.pdf")
    with open(path, "rb") as f:
        response = client.post(
            "/inspect/location",
            data={"field": "missing_name"},
            files={"pdf": ("sample_template.pdf", f, "application/pdf")},
        )

    assert_web_api_error(
        response,
        404,
        "Form field 'missing_name' does not exist",
    )
