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
def image_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "image_samples")


@pytest.fixture
def image_stream(image_samples):
    with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as f:
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


def test_fill_font_20_v2(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled_font_20.pdf"), "rb+") as f:
        obj = PyPDFForm2(template_stream, global_font_size=20).fill(
            data_dict,
        )

        expected = f.read()

        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == ElementType.text:
                assert v.font == TextConstants().global_font
                assert v.font_size == 20
                assert v.font_color == TextConstants().global_font_color
                assert v.text_x_offset == TextConstants().global_text_x_offset
                assert v.text_y_offset == TextConstants().global_text_y_offset
                assert v.text_wrap_length == TextConstants().global_text_wrap_length


def test_fill_font_color_red_v2(template_stream, pdf_samples, data_dict):
    with open(
        os.path.join(pdf_samples, "sample_filled_font_color_red.pdf"), "rb+"
    ) as f:
        obj = PyPDFForm2(
            template_stream, global_font_color=(1, 0, 0)
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
                assert v.font == TextConstants().global_font
                assert v.font_size == TextConstants().global_font_size
                assert v.font_color == (1, 0, 0)
                assert v.text_x_offset == TextConstants().global_text_x_offset
                assert v.text_y_offset == TextConstants().global_text_y_offset
                assert v.text_wrap_length == TextConstants().global_text_wrap_length


def test_fill_offset_100_v2(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled_offset_100.pdf"), "rb+") as f:
        obj = PyPDFForm2(
            template_stream,
            global_text_x_offset=100,
            global_text_y_offset=-100,
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
                assert v.font == TextConstants().global_font
                assert v.font_size == TextConstants().global_font_size
                assert v.font_color == TextConstants().global_font_color
                assert v.text_x_offset == 100
                assert v.text_y_offset == -100
                assert v.text_wrap_length == TextConstants().global_text_wrap_length


def test_fill_wrap_2_v2(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled_text_wrap_2.pdf"), "rb+") as f:
        obj = PyPDFForm2(
            template_stream, global_text_wrap_length=2
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
                assert v.font == TextConstants().global_font
                assert v.font_size == TextConstants().global_font_size
                assert v.font_color == TextConstants().global_font_color
                assert v.text_x_offset == TextConstants().global_text_x_offset
                assert v.text_y_offset == TextConstants().global_text_y_offset
                assert v.text_wrap_length == 2


def test_fill_with_customized_elements_v2(
    template_stream, pdf_samples, data_dict
):
    with open(
        os.path.join(pdf_samples, "sample_filled_customized_elements.pdf"), "rb+"
    ) as f:
        obj = PyPDFForm2(template_stream)

        obj.elements["test"].font = "LiberationSerif-Italic"
        obj.elements["test"].font_size = 20
        obj.elements["test"].font_color = (1, 0, 0)
        obj.elements["test_2"].font_color = (0, 1, 0)
        obj.elements["test_2"].text_x_offset = 50
        obj.elements["test_2"].text_y_offset = -50
        obj.elements["test_2"].text_wrap_length = 1
        obj.elements["test_3"].text_wrap_length = 2

        obj.fill(data_dict)

        expected = f.read()

        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

        assert obj.elements["test"].font == "LiberationSerif-Italic"
        assert obj.elements["test"].font_size == 20
        assert obj.elements["test"].font_color == (1, 0, 0)
        assert (
            obj.elements["test"].text_x_offset == TextConstants().global_text_x_offset
        )
        assert (
            obj.elements["test"].text_y_offset == TextConstants().global_text_y_offset
        )
        assert (
            obj.elements["test"].text_wrap_length
            == TextConstants().global_text_wrap_length
        )

        assert obj.elements["test_2"].font_size == TextConstants().global_font_size
        assert obj.elements["test_2"].font_color == (0, 1, 0)
        assert obj.elements["test_2"].text_x_offset == 50
        assert obj.elements["test_2"].text_y_offset == -50
        assert obj.elements["test_2"].text_wrap_length == 1

        assert obj.elements["test_3"].font_size == TextConstants().global_font_size
        assert obj.elements["test_3"].font_color == TextConstants().global_font_color
        assert (
            obj.elements["test_3"].text_x_offset == TextConstants().global_text_x_offset
        )
        assert (
            obj.elements["test_3"].text_y_offset == TextConstants().global_text_y_offset
        )
        assert obj.elements["test_3"].text_wrap_length == 2


def test_fill_radiobutton_v2(pdf_samples, template_with_radiobutton_stream):
    with open(os.path.join(pdf_samples, "sample_filled_radiobutton.pdf"), "rb+") as f:
        obj = PyPDFForm2(template_with_radiobutton_stream).fill(
            {
                "radio_1": 0,
                "radio_2": 1,
                "radio_3": 2,
            },
        )

        assert obj.stream == f.read()


def test_fill_sejda_and_read_v2(sejda_template, pdf_samples, sejda_data):
    with open(os.path.join(pdf_samples, "sample_filled_sejda.pdf"), "rb+") as f:
        obj = PyPDFForm2(sejda_template).fill(
            sejda_data,
        )
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_draw_text_on_one_page_v2(template_stream, pdf_samples):
    with open(os.path.join(pdf_samples, "sample_pdf_with_drawn_text.pdf"), "rb+") as f:
        obj = PyPDFForm2(template_stream).draw_text(
            "drawn_text",
            1,
            300,
            225,
            font=TextConstants().global_font,
            font_size=20,
            font_color=(1, 0, 0),
            text_x_offset=50,
            text_y_offset=50,
            text_wrap_length=4,
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected
