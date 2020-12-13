# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from reportlab.pdfgen import canvas

from PyPDFForm.core.watermark import Watermark as WatermarkCore


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "v2")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def image_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_image.jpg"), "rb+") as f:
        return f.read()


def test_draw_image(image_stream):
    buff = BytesIO()

    c = canvas.Canvas(buff, pagesize=(100, 100))

    WatermarkCore().draw_image(c, image_stream, 100, 100, 400, 225)

    c.save()
    buff.seek(0)

    assert buff.read()

    buff.close()


def create_watermarks_and_draw_images(template_stream, image_stream):
    page_number = 2

    watermarks = WatermarkCore().create_watermarks_and_draw(
        template_stream,
        page_number,
        "image",
        [
            [
                image_stream,
                0,
                0,
                400,
                225,
            ]
        ],
    )

    for i in range(len(watermarks)):
        if i == page_number - 1:
            assert watermarks[i]
        else:
            assert not watermarks[i]

    watermarks_drawn_two_images = WatermarkCore().create_watermarks_and_draw(
        template_stream,
        page_number,
        "image",
        [
            [
                image_stream,
                0,
                0,
                400,
                225,
            ],
            [
                image_stream,
                0,
                225,
                400,
                225,
            ],
        ],
    )

    assert watermarks[page_number - 1] != watermarks_drawn_two_images[page_number - 1]


def test_merge_watermarks_with_pdf(template_stream, image_stream):
    watermarks = WatermarkCore().create_watermarks_and_draw(
        template_stream,
        2,
        "image",
        [
            [
                image_stream,
                0,
                0,
                400,
                225,
            ]
        ],
    )

    assert template_stream != WatermarkCore().merge_watermarks_with_pdf(
        template_stream, watermarks
    )