# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader

from PyPDFForm.api import app
from PyPDFForm.lib.constants import Title

client = TestClient(app)


@pytest.mark.web_api_test
def test_change_title(static_pdfs):
    path = os.path.join(static_pdfs, "sample_template.pdf")
    with open(path, "rb") as f:
        response = client.post(
            "/update/title",
            data={"new_title": "My PDF"},
            files={
                "pdf": ("sample_template.pdf", f, "application/pdf"),
            },
        )

    assert response.status_code == 200

    reader = PdfReader(BytesIO(response.content))
    assert (reader.metadata or {}).get(Title) == "My PDF"
