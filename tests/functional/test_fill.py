# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm.middleware.wrapper import PyPDFForm
from PyPDFForm.middleware.element import ElementType
from PyPDFForm.middleware.constants import Text as TextConstants


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "v2")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


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


def test_fill_simple_mode(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled_simple_mode.pdf"), "rb+") as f:
        obj = PyPDFForm(template_stream).fill(
            data_dict,
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_simple_mode_editable(template_stream, pdf_samples, data_dict):
    with open(
        os.path.join(pdf_samples, "sample_filled_simple_mode_editable.pdf"), "rb+"
    ) as f:
        obj = PyPDFForm(template_stream).fill(
            data_dict,
            editable=True,
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_non_simple_mode_font_20(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled_font_20.pdf"), "rb+") as f:
        obj = PyPDFForm(template_stream, simple_mode=False, global_font_size=20).fill(
            data_dict,
        )

        expected = f.read()

        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == ElementType.text:
                assert v.font_size == 20
                assert v.font_color == TextConstants().global_font_color
                assert v.text_x_offset == TextConstants().global_text_x_offset
                assert v.text_y_offset == TextConstants().global_text_y_offset
                assert v.text_wrap_length == TextConstants().global_text_wrap_length


def test_fill_non_simple_mode_font_color_red(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled_font_color_red.pdf"), "rb+") as f:
        obj = PyPDFForm(template_stream, simple_mode=False, global_font_color=(1, 0, 0)).fill(
            data_dict,
        )

        expected = f.read()

        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == ElementType.text:
                assert v.font_size == TextConstants().global_font_size
                assert v.font_color == (1, 0, 0)
                assert v.text_x_offset == TextConstants().global_text_x_offset
                assert v.text_y_offset == TextConstants().global_text_y_offset
                assert v.text_wrap_length == TextConstants().global_text_wrap_length


def test_fill_non_simple_mode_offset_100(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled_offset_100.pdf"), "rb+") as f:
        obj = PyPDFForm(template_stream, simple_mode=False, global_text_x_offset=100, global_text_y_offset=-100).fill(
            data_dict,
        )

        expected = f.read()

        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == ElementType.text:
                assert v.font_size == TextConstants().global_font_size
                assert v.font_color == TextConstants().global_font_color
                assert v.text_x_offset == 100
                assert v.text_y_offset == -100
                assert v.text_wrap_length == TextConstants().global_text_wrap_length
