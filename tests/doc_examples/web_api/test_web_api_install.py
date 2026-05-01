# -*- coding: utf-8 -*-

import os

import pytest
from fastapi.testclient import TestClient

from PyPDFForm.api import app

client = TestClient(app)


@pytest.mark.web_api_test
def test_use_full_widget_name_option(static_pdfs):
    path = os.path.join(static_pdfs, "sample_template_with_full_key.pdf")
    with open(path, "rb") as f:
        response = client.post(
            "/inspect/location",
            params={"use_full_widget_name": True},
            data={"field": "Gain de 2 classes.0"},
            files={
                "pdf": ("sample_template_with_full_key.pdf", f, "application/pdf"),
            },
        )

    assert response.status_code == 200
