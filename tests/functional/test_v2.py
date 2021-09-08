# -*- coding: utf-8 -*-

import os
import random

import pytest

from PyPDFForm import PyPDFForm2
from PyPDFForm.middleware.constants import Text as TextConstants
from PyPDFForm.middleware.element import ElementType


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "v2")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def template_with_radiobutton_stream(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_radio_button.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def font_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "font_samples")


@pytest.fixture
def data_dict():
    return {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    }


def test_fill_v2(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled.pdf"), "rb+") as f:
        obj = PyPDFForm2(template_stream).fill(
            data_dict,
        )
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_font_liberation_serif_italic_v2(
    template_stream, pdf_samples, font_samples, data_dict
):
    with open(os.path.join(font_samples, "LiberationSerif-Italic.ttf"), "rb+") as _f:
        stream = _f.read()
        _f.seek(0)
        PyPDFForm2.register_font(
            "LiberationSerif-Italic",
            random.choice(
                [os.path.join(font_samples, "LiberationSerif-Italic.ttf"), _f, stream]
            ),
        )

    with open(
        os.path.join(pdf_samples, "sample_filled_font_liberation_serif_italic.pdf"),
        "rb+",
    ) as f:
        obj = PyPDFForm2(
            template_stream, global_font="LiberationSerif-Italic"
        ).fill(
            data_dict,
        )

        expected = f.read()

        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == ElementType.text:
                assert v.font == "LiberationSerif-Italic"
                assert v.font_size == TextConstants().global_font_size
                assert v.font_color == TextConstants().global_font_color
                assert v.text_x_offset == TextConstants().global_text_x_offset
                assert v.text_y_offset == TextConstants().global_text_y_offset
                assert v.text_wrap_length == TextConstants().global_text_wrap_length
