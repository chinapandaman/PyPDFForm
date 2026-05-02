# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader

from PyPDFForm.api import app
from PyPDFForm.lib.constants import AcroForm, Title

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


@pytest.mark.web_api_test
def test_need_appearances_option(static_pdfs):
    path = os.path.join(static_pdfs, "sample_template.pdf")
    with open(path, "rb") as f:
        response = client.post(
            "/update/title",
            params={"need_appearances": True},
            data={"new_title": "My PDF"},
            files={
                "pdf": ("sample_template.pdf", f, "application/pdf"),
            },
        )

    assert response.status_code == 200

    reader = PdfReader(BytesIO(response.content))
    assert reader.root_object[AcroForm]["/NeedAppearances"]


@pytest.mark.web_api_test
def test_generate_appearance_streams_option(static_pdfs):
    path = os.path.join(static_pdfs, "sample_template.pdf")
    with open(path, "rb") as f:
        response = client.post(
            "/update/title",
            params={"generate_appearance_streams": True},
            data={"new_title": "My PDF"},
            files={
                "pdf": ("sample_template.pdf", f, "application/pdf"),
            },
        )

    assert response.status_code == 200

    reader = PdfReader(BytesIO(response.content))
    assert "/NeedAppearances" not in reader.root_object[AcroForm]


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
