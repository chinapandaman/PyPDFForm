# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm.middleware.wrapper import PyPDFForm


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


def test_draw_image_on_one_page(template_stream, image_stream, pdf_samples):
    with open(os.path.join(pdf_samples, "sample_pdf_with_image.pdf"), "rb+") as f:
        obj = PyPDFForm(template_stream).draw_image(image_stream, 2, 100, 100, 400, 300)

        expected = f.read()

        if os.name == "nt":
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected
        else:
            assert obj.stream[:32767] == expected[:32767]
