# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from reportlab.pdfgen import canvas

from PyPDFForm.core import watermark as watermark_core
from PyPDFForm.core import watermark as watermark_core
from PyPDFForm.middleware.constants import Text as TextConstants
from PyPDFForm.middleware.element import Element as ElementMiddleware
from PyPDFForm.middleware.element import ElementType


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples")


@pytest.fixture
def image_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "image_samples")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def image_stream(image_samples):
    with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as f:
        return f.read()


@pytest.fixture
def text_element():
    new_element = ElementMiddleware("new", ElementType.text)
    new_element.value = "drawn_text"
    new_element.font = TextConstants().global_font
    new_element.font_size = TextConstants().global_font_size
    new_element.font_color = TextConstants().global_font_color
    new_element.text_x_offset = TextConstants().global_text_x_offset
    new_element.text_y_offset = TextConstants().global_text_y_offset
    new_element.text_wrap_length = TextConstants().global_text_wrap_length
    new_element.validate_constants()
    new_element.validate_value()
    new_element.validate_text_attributes()

    return new_element


def test_draw_text(text_element):
    buff = BytesIO()

    assert not buff.read()
    buff.seek(0)

    c = canvas.Canvas(buff, pagesize=(100, 100))

    watermark_core.draw_text(
        c,
        text_element,
        300,
        225,
    )

    c.save()
    buff.seek(0)

    assert buff.read()

    buff.close()


def test_draw_image(image_stream):
    buff = BytesIO()

    assert not buff.read()
    buff.seek(0)

    c = canvas.Canvas(buff, pagesize=(100, 100))

    watermark_core.draw_image(c, image_stream, 100, 100, 400, 225)

    c.save()
    buff.seek(0)

    assert buff.read()

    buff.close()


def test_create_watermarks_and_draw_texts(template_stream, text_element):
    page_number = 2

    watermarks = watermark_core.create_watermarks_and_draw(
        template_stream,
        page_number,
        "text",
        [
            [
                text_element,
                300,
                225,
            ]
        ],
    )

    for i in range(len(watermarks)):
        if i == page_number - 1:
            assert watermarks[i]
        else:
            assert not watermarks[i]

    watermarks_drawn_two_texts = watermark_core.create_watermarks_and_draw(
        template_stream,
        page_number,
        "text",
        [
            [
                text_element,
                300,
                225,
            ],
            [
                text_element,
                400,
                225,
            ],
        ],
    )

    assert watermarks[page_number - 1] != watermarks_drawn_two_texts[page_number - 1]


def test_create_watermarks_and_draw_images(template_stream, image_stream):
    page_number = 2

    watermarks = watermark_core.create_watermarks_and_draw(
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

    watermarks_drawn_two_images = watermark_core.create_watermarks_and_draw(
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
    watermarks = watermark_core.create_watermarks_and_draw(
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

    assert template_stream != watermark_core.merge_watermarks_with_pdf(
        template_stream, watermarks
    )
