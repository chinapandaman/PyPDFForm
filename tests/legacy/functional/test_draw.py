# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import PyPDFForm


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "../..", "..", "pdf_samples")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def image_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_image.jpg"), "rb+") as f:
        return f.read()


@pytest.fixture
def comparing_size():
    return 32767


def test_draw_image_on_one_page(
    template_stream, image_stream, pdf_samples, comparing_size
):
    with open(os.path.join(pdf_samples, "sample_pdf_with_image.pdf"), "rb+") as f:
        obj = (
            PyPDFForm(template_stream)
            .fill(
                {
                    "test": "test_1",
                    "check": True,
                    "test_2": "test_2",
                    "check_2": False,
                    "test_3": "test_3",
                    "check_3": True,
                },
            )
            .draw_image(image_stream, 2, 100, 100, 400, 225, 0)
        )

        expected = f.read()

        assert obj.stream[:comparing_size] == expected[:comparing_size]


def test_draw_text_on_one_page(template_stream, pdf_samples, comparing_size):
    with open(os.path.join(pdf_samples, "sample_pdf_with_drawn_text.pdf"), "rb+") as f:
        obj = (
            PyPDFForm(template_stream)
            .fill(
                {
                    "test": "test_1",
                    "check": True,
                    "test_2": "test_2",
                    "check_2": False,
                    "test_3": "test_3",
                    "check_3": True,
                },
            )
            .draw_text("drawn_text", 1, 300, 225)
        )

        expected = f.read()

        assert len(str(obj.stream)) == len(str(expected))
        assert str(obj.stream)[:comparing_size] == str(expected)[:comparing_size]
