# -*- coding: utf-8 -*-

import json
import os

import pytest
from fastapi.testclient import TestClient

from PyPDFForm.api import app

client = TestClient(app)


@pytest.mark.web_api_test
def test_fill_text_check(pdf_samples, static_pdfs, json_samples):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_text_check.pdf")
    path = os.path.join(static_pdfs, "sample_template.pdf")
    with (
        open(path, "rb") as f,
        open(os.path.join(json_samples, "test_fill_text_check.json"), "r") as j,
    ):
        result = client.post(
            "/fill",
            data={"data": json.dumps(json.load(j))},
            files={
                "pdf": ("output.pdf", f, "application/pdf"),
            },
        )

    with open(expected_path, "rb") as f:
        expected = f.read()
        actual = result.content

        assert len(expected) == len(actual)
        assert expected == actual
