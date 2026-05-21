# -*- coding: utf-8 -*-

import json
import os

import pytest
from fastapi.testclient import TestClient

from PyPDFForm.api import app

client = TestClient(app)


def write_invalid_json(tmp_path, content):
    data_path = tmp_path / "invalid.json"
    data_path.write_text(content, encoding="utf-8")
    return str(data_path)


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
def test_fill_wrong_known_field_type(pdf_samples, tmp_path):
    data_path = write_invalid_json(tmp_path, '{"check": "yes"}')
    path = os.path.join(pdf_samples, "sample_template.pdf")
    with (
        open(path, "rb") as f,
        open(data_path, "r") as j,
    ):
        response = client.post(
            "/fill",
            data={"data": json.dumps(json.load(j))},
            files={
                "pdf": ("output.pdf", f, "application/pdf"),
            },
        )

    assert_web_api_error(response, 400, "Invalid JSON at check")


@pytest.mark.web_api_test
def test_create_extract_start_after_end(pdf_samples):
    path = os.path.join(pdf_samples, "sample_template.pdf")
    with open(path, "rb") as f:
        response = client.post(
            "/create/extract",
            data={"start": 3, "end": 1},
            files={"pdf": ("sample_template.pdf", f, "application/pdf")},
        )

    assert_web_api_error(
        response, 400, "End page must be greater than or equal to start page."
    )


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
