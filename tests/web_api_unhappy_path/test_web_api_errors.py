# -*- coding: utf-8 -*-

import pytest
from fastapi.testclient import TestClient

from PyPDFForm.api import app

client = TestClient(app)


@pytest.mark.web_api_test
def test_index_redirect_to_docs():
    response = client.get("/")

    assert response.status_code == 200
    assert b"Swagger UI" in response.content
