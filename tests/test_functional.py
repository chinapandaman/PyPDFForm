# -*- coding: utf-8 -*-

import os

import pytest
from jsonschema import ValidationError, validate

from PyPDFForm import PyPDFForm2
from PyPDFForm.core import template as template_core
from PyPDFForm.middleware import constants
from PyPDFForm.middleware.element import ElementType


def test_fill(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled.pdf"), "rb+") as f:
        obj = PyPDFForm2(template_stream).fill(
            data_dict,
        )
        assert len(obj.read()) == len(obj.stream)
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected

        for page, elements in template_core.get_elements_by_page(obj.read()).items():
            assert not elements


def test_register_bad_fonts():
    assert not PyPDFForm2.register_font("foo", b"foo")
    assert not PyPDFForm2.register_font("foo", "foo")


def test_fill_font_liberation_serif_italic(
    template_stream, pdf_samples, font_samples, data_dict
):
    with open(os.path.join(font_samples, "LiberationSerif-Italic.ttf"), "rb+") as _f:
        stream = _f.read()
        _f.seek(0)
        PyPDFForm2.register_font(
            "LiberationSerif-Italic",
            stream
        )

    with open(
        os.path.join(pdf_samples, "sample_filled_font_liberation_serif_italic.pdf"),
        "rb+",
    ) as f:
        obj = PyPDFForm2(template_stream, global_font="LiberationSerif-Italic").fill(
            data_dict,
        )

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == ElementType.text:
                assert v.font == "LiberationSerif-Italic"
                assert v.font_size == constants.GLOBAL_FONT_SIZE
                assert v.font_color == constants.GLOBAL_FONT_COLOR
                assert v.text_x_offset == constants.GLOBAL_TEXT_X_OFFSET
                assert v.text_y_offset == constants.GLOBAL_TEXT_Y_OFFSET
                assert v.text_wrap_length == constants.GLOBAL_TEXT_WRAP_LENGTH


def test_fill_font_20(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled_font_20.pdf"), "rb+") as f:
        obj = PyPDFForm2(template_stream, global_font_size=20).fill(
            data_dict,
        )

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == ElementType.text:
                assert v.font == constants.GLOBAL_FONT
                assert v.font_size == 20
                assert v.font_color == constants.GLOBAL_FONT_COLOR
                assert v.text_x_offset == constants.GLOBAL_TEXT_X_OFFSET
                assert v.text_y_offset == constants.GLOBAL_TEXT_Y_OFFSET
                assert v.text_wrap_length == constants.GLOBAL_TEXT_WRAP_LENGTH


def test_fill_font_color_red(template_stream, pdf_samples, data_dict):
    with open(
        os.path.join(pdf_samples, "sample_filled_font_color_red.pdf"), "rb+"
    ) as f:
        obj = PyPDFForm2(template_stream, global_font_color=(1, 0, 0)).fill(
            data_dict,
        )

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == ElementType.text:
                assert v.font == constants.GLOBAL_FONT
                assert v.font_size == constants.GLOBAL_FONT_SIZE
                assert v.font_color == (1, 0, 0)
                assert v.text_x_offset == constants.GLOBAL_TEXT_X_OFFSET
                assert v.text_y_offset == constants.GLOBAL_TEXT_Y_OFFSET
                assert v.text_wrap_length == constants.GLOBAL_TEXT_WRAP_LENGTH


def test_fill_offset_100(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled_offset_100.pdf"), "rb+") as f:
        obj = PyPDFForm2(
            template_stream,
            global_text_x_offset=100,
            global_text_y_offset=-100,
        ).fill(
            data_dict,
        )

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == ElementType.text:
                assert v.font == constants.GLOBAL_FONT
                assert v.font_size == constants.GLOBAL_FONT_SIZE
                assert v.font_color == constants.GLOBAL_FONT_COLOR
                assert v.text_x_offset == 100
                assert v.text_y_offset == -100
                assert v.text_wrap_length == constants.GLOBAL_TEXT_WRAP_LENGTH


def test_fill_wrap_2(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled_text_wrap_2.pdf"), "rb+") as f:
        obj = PyPDFForm2(template_stream, global_text_wrap_length=2).fill(
            data_dict,
        )

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == ElementType.text:
                assert v.font == constants.GLOBAL_FONT
                assert v.font_size == constants.GLOBAL_FONT_SIZE
                assert v.font_color == constants.GLOBAL_FONT_COLOR
                assert v.text_x_offset == constants.GLOBAL_TEXT_X_OFFSET
                assert v.text_y_offset == constants.GLOBAL_TEXT_Y_OFFSET
                assert v.text_wrap_length == 2


def test_fill_with_customized_elements(template_stream, pdf_samples, data_dict):
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

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

        assert obj.elements["test"].font == "LiberationSerif-Italic"
        assert obj.elements["test"].font_size == 20
        assert obj.elements["test"].font_color == (1, 0, 0)
        assert obj.elements["test"].text_x_offset == constants.GLOBAL_TEXT_X_OFFSET
        assert obj.elements["test"].text_y_offset == constants.GLOBAL_TEXT_Y_OFFSET
        assert (
            obj.elements["test"].text_wrap_length == constants.GLOBAL_TEXT_WRAP_LENGTH
        )

        assert obj.elements["test_2"].font_size == constants.GLOBAL_FONT_SIZE
        assert obj.elements["test_2"].font_color == (0, 1, 0)
        assert obj.elements["test_2"].text_x_offset == 50
        assert obj.elements["test_2"].text_y_offset == -50
        assert obj.elements["test_2"].text_wrap_length == 1

        assert obj.elements["test_3"].font_size == constants.GLOBAL_FONT_SIZE
        assert obj.elements["test_3"].font_color == constants.GLOBAL_FONT_COLOR
        assert obj.elements["test_3"].text_x_offset == constants.GLOBAL_TEXT_X_OFFSET
        assert obj.elements["test_3"].text_y_offset == constants.GLOBAL_TEXT_Y_OFFSET
        assert obj.elements["test_3"].text_wrap_length == 2


def test_fill_radiobutton(pdf_samples, template_with_radiobutton_stream):
    with open(os.path.join(pdf_samples, "sample_filled_radiobutton.pdf"), "rb+") as f:
        obj = PyPDFForm2(template_with_radiobutton_stream).fill(
            {
                "radio_1": 0,
                "radio_2": 1,
                "radio_3": 2,
            },
        )

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_fill_sejda_and_read(sejda_template, pdf_samples, sejda_data):
    with open(os.path.join(pdf_samples, "sample_filled_sejda.pdf"), "rb+") as f:
        obj = PyPDFForm2(sejda_template).fill(
            sejda_data,
        )
        assert len(obj.read()) == len(obj.stream)
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_draw_text_on_one_page(template_stream, pdf_samples):
    with open(os.path.join(pdf_samples, "sample_pdf_with_drawn_text.pdf"), "rb+") as f:
        obj = PyPDFForm2(template_stream).draw_text(
            "drawn_text",
            1,
            300,
            225,
            font=constants.GLOBAL_FONT,
            font_size=20,
            font_color=(1, 0, 0),
            text_x_offset=50,
            text_y_offset=50,
            text_wrap_length=4,
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
        PyPDFForm2.register_font("LiberationSerif-BoldItalic", _f.read())

    with open(
        os.path.join(pdf_samples, "sample_pdf_with_drawn_text_different_font.pdf"),
        "rb+",
    ) as f:
        obj = PyPDFForm2(template_stream).draw_text(
            "drawn_text",
            1,
            300,
            225,
            font="LiberationSerif-BoldItalic",
            font_size=20,
            font_color=(1, 0, 0),
            text_x_offset=50,
            text_y_offset=50,
            text_wrap_length=4,
        )

        expected = f.read()

        if os.name == "nt":
            assert len(obj.stream) == len(expected)
        else:
            with open(
                os.path.join(
                    pdf_samples, "sample_pdf_with_drawn_text_different_font_linux.pdf"
                ),
                "rb+",
            ) as f_linux:
                expected = f_linux.read()
                assert len(obj.stream) == len(expected)
                assert obj.stream == expected


def test_draw_image_on_one_page(template_stream, image_samples, pdf_samples):
    with open(os.path.join(pdf_samples, "sample_pdf_with_image.pdf"), "rb+") as f:
        with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as _f:
            obj = PyPDFForm2(template_stream).draw_image(
                _f,
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


def test_draw_png_image_on_one_page(template_stream, image_samples, pdf_samples):
    with open(os.path.join(pdf_samples, "sample_pdf_with_png_image.pdf"), "rb+") as f:
        obj = PyPDFForm2(template_stream).draw_image(
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


def test_addition_operator_3_times(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_added_3_copies.pdf"), "rb+") as f:
        result = PyPDFForm2()

        for i in range(3):
            result += PyPDFForm2(template_stream).fill(data_dict)

        expected = f.read()
        assert len(result.read()) == len(expected)
        assert result.read() == expected
        assert len((result + PyPDFForm2()).read()) == len(result.read())
        assert (result + PyPDFForm2()).read() == result.read()


def test_addition_operator_3_times_sejda(sejda_template, pdf_samples, sejda_data):
    with open(os.path.join(pdf_samples, "sample_added_3_copies_sejda.pdf"), "rb+") as f:
        result = PyPDFForm2()

        for i in range(3):
            result += PyPDFForm2(sejda_template).fill(sejda_data)

        expected = f.read()
        assert len(result.read()) == len(expected)
        assert result.read() == expected


def test_generate_schema(sample_template_with_comb_text_field):
    data = {
        "FirstName": "John",
        "MiddleName": "Joe",
        "LastName": "XXXXXXX",
        "Awesomeness": True,
        "Gender": 0,
    }
    schema = PyPDFForm2(sample_template_with_comb_text_field).generate_schema()

    assert schema["type"] == "object"
    properties = schema["properties"]
    for key, value in data.items():
        if key == "LastName":
            assert properties[key]["maxLength"] == 7
        if isinstance(value, str):
            assert properties[key]["type"] == "string"
        elif isinstance(value, bool):
            assert properties[key]["type"] == "boolean"
        elif isinstance(value, int):
            assert properties[key]["type"] == "integer"
            assert properties[key]["maximum"] == 1

    validate(instance=data, schema=schema)
    assert True

    data["LastName"] = "XXXXXXXX"
    try:
        validate(instance=data, schema=schema)
        assert False
    except ValidationError:
        assert True

    data["LastName"] = "XXXXXXX"
    data["Gender"] = 1
    validate(instance=data, schema=schema)
    assert True

    data["Gender"] = 2
    try:
        validate(instance=data, schema=schema)
        assert False
    except ValidationError:
        assert True


def test_fill_right_aligned(sample_template_with_right_aligned_text_field, pdf_samples):
    with open(os.path.join(pdf_samples, "sample_filled_right_aligned.pdf"), "rb+") as f:
        obj = PyPDFForm2(sample_template_with_right_aligned_text_field).fill(
            {
                "name": "Hans Mustermann",
                "fulladdress": "Musterstr. 12, 82903 Musterdorf, Musterland",
                "advisorname": "Karl Test",
            },
        )
        assert len(obj.read()) == len(obj.stream)
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected

        for page, elements in template_core.get_elements_by_page(obj.read()).items():
            assert not elements
