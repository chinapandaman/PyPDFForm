# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import PyPDFForm
from PyPDFForm.middleware.constants import Text as TextConstants


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples")


@pytest.fixture
def image_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "image_samples")


@pytest.fixture
def font_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "font_samples")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def image_stream(image_samples):
    with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as f:
        return f.read()


def test_draw_text_on_one_page(template_stream, pdf_samples):
    with open(os.path.join(pdf_samples, "sample_pdf_with_drawn_text.pdf"), "rb+") as f:
        obj = PyPDFForm(template_stream).draw_text(
            "drawn_text",
            1,
            300,
            225,
            TextConstants().global_font,
            20,
            (1, 0, 0),
            50,
            50,
            4,
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_draw_text_on_one_page_different_font(
    template_stream, pdf_samples, font_samples
):
    with open(
        os.path.join(font_samples, "LiberationSerif-BoldItalic.ttf"), "rb+"
    ) as _f:
        PyPDFForm.register_font("LiberationSerif-BoldItalic", _f.read())

    with open(
        os.path.join(pdf_samples, "sample_pdf_with_drawn_text_different_font.pdf"),
        "rb+",
    ) as f:
        obj = PyPDFForm(template_stream).draw_text(
            "drawn_text",
            1,
            300,
            225,
            "LiberationSerif-BoldItalic",
            20,
            (1, 0, 0),
            50,
            50,
            4,
        )

        expected = f.read()

        if os.name == "nt":
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected
        else:
            with open(
                    os.path.join(pdf_samples, "sample_pdf_with_drawn_text_different_font_linux.pdf"),
                    "rb+",
            ) as f_linux:
                expected = f_linux.read()
                assert len(obj.stream) == len(expected)
                assert obj.stream == expected


def test_draw_image_on_one_page(template_stream, image_stream, pdf_samples):
    with open(os.path.join(pdf_samples, "sample_pdf_with_image.pdf"), "rb+") as f:
        obj = PyPDFForm(template_stream).draw_image(image_stream, 2, 100, 100, 400, 225)

        expected = f.read()

    if os.name == "nt":
        assert len(obj.stream) == len(expected)
        assert obj.stream == expected
    else:
        with open(os.path.join(pdf_samples, "sample_pdf_with_image_linux.pdf"), "rb+") as f_linux:
            expected = f_linux.read()
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected


def test_draw_image_on_one_page_fp_param(template_stream, image_samples, pdf_samples):
    with open(os.path.join(pdf_samples, "sample_pdf_with_image.pdf"), "rb+") as f:
        expected = f.read()

    obj = PyPDFForm(template_stream).draw_image(
        os.path.join(image_samples, "sample_image.jpg"), 2, 100, 100, 400, 225
    )

    if os.name == "nt":
        assert len(obj.stream) == len(expected)
        assert obj.stream == expected
    else:
        with open(os.path.join(pdf_samples, "sample_pdf_with_image_linux.pdf"), "rb+") as f_linux:
            expected = f_linux.read()
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected


def test_draw_image_on_one_page_f_obj_param(
    template_stream, image_samples, pdf_samples
):
    with open(os.path.join(pdf_samples, "sample_pdf_with_image.pdf"), "rb+") as f:
        expected = f.read()

    with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as image:
        obj = PyPDFForm(template_stream).draw_image(image, 2, 100, 100, 400, 225)

    if os.name == "nt":
        assert len(obj.stream) == len(expected)
        assert obj.stream == expected
    else:
        with open(os.path.join(pdf_samples, "sample_pdf_with_image_linux.pdf"), "rb+") as f_linux:
            expected = f_linux.read()
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected


def test_draw_png_image_on_one_page(template_stream, image_samples, pdf_samples):
    with open(os.path.join(pdf_samples, "sample_pdf_with_png_image.pdf"), "rb+") as f:
        obj = PyPDFForm(template_stream).draw_image(
            os.path.join(image_samples, "before_converted.png"),
            2,
            100,
            100,
            400,
            225,
        )

        expected = f.read()

        if os.name == "nt":
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected
        else:
            with open(os.path.join(pdf_samples, "sample_pdf_with_png_image_linux.pdf"), "rb+") as f_linux:
                expected = f_linux.read()
                assert len(obj.stream) == len(expected)
                assert obj.stream == expected
