# -*- coding: utf-8 -*-

import os
import pytest

from PyPDFForm.core.watermark import Watermark as WatermarkCore
from reportlab.pdfgen import canvas
from io import BytesIO


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "v2")


@pytest.fixture
def image_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_image.jpg"), "rb+") as f:
        return f.read()


def test_draw_image(image_stream):
    buff = BytesIO()

    c = canvas.Canvas(
        buff,
        pagesize=(
            100,
            100
        )
    )

    WatermarkCore().draw_image(c, image_stream, 0, 0, 400, 225)

    c.save()
    buff.seek(0)

    assert buff.read()

    buff.close()
