# -*- coding: utf-8 -*-

import os
import pytest
from PyPDFForm.core.image import Image as ImageCore
from PIL import Image
from io import BytesIO


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "v2")


@pytest.fixture
def image_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_image.jpg"), "rb+") as f:
        return f.read()


def test_rotate_image(image_stream):
    rotated = ImageCore().rotate_image(image_stream, 180)

    assert rotated != image_stream

    buff = BytesIO()
    buff.write(image_stream)
    buff.seek(0)

    rotated_buff = BytesIO()
    rotated_buff.write(rotated)
    rotated_buff.seek(0)

    assert Image.open(buff).format == Image.open(rotated_buff).format

    buff.close()
    rotated_buff.close()
