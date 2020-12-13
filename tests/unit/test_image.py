# -*- coding: utf-8 -*-

import os
import pytest
from PyPDFForm.core.image import Image as ImageCore


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "v2")


@pytest.fixture
def image_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_image.jpg"), "rb+") as f:
        return f.read()


def test_rotate_image(image_stream):
    assert ImageCore().rotate_image(image_stream, 180) != image_stream
