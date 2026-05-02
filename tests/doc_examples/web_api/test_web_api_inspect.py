# -*- coding: utf-8 -*-

import json
import os

import pytest
from fastapi.testclient import TestClient

from PyPDFForm.api import app

client = TestClient(app)


@pytest.mark.web_api_test
def test_schema(static_pdfs):
    path = os.path.join(static_pdfs, "sample_template.pdf")
    with open(path, "rb") as f:
        response = client.post(
            "/inspect/schema",
            files={
                "pdf": ("sample_template.pdf", f, "application/pdf"),
            },
        )

    assert response.status_code == 200

    assert json.loads(response.content) == {
        "type": "object",
        "properties": {
            "test": {"type": "string"},
            "check": {"type": "boolean"},
            "test_2": {"type": "string"},
            "check_2": {"type": "boolean"},
            "test_3": {"type": "string"},
            "check_3": {"type": "boolean"},
        },
        "additionalProperties": True,
    }


@pytest.mark.web_api_test
def test_data(static_pdfs):
    path = os.path.join(static_pdfs, "sample_template_filled.pdf")
    with open(path, "rb") as f:
        response = client.post(
            "/inspect/data",
            files={
                "pdf": ("sample_template_filled.pdf", f, "application/pdf"),
            },
        )

    assert response.status_code == 200

    assert json.loads(response.content) == {
        "check": True,
        "check_2": True,
        "check_3": True,
        "test": "test",
        "test_2": "test2",
        "test_3": "test3",
    }
