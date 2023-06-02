# -*- coding: utf-8 -*-

import os

from jsonschema import ValidationError, validate

from PyPDFForm import PyPDFForm
from PyPDFForm.core import template as template_core
from PyPDFForm.middleware import constants
from PyPDFForm.middleware.element import Element
from PyPDFForm.middleware.text import Text


def test_base_schema_definition():
    try:
        assert Element("foo").schema_definition
        assert False
    except NotImplementedError:
        pass


def test_fill(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "sample_filled.pdf")
    with open(expected_path, "rb+") as f:
        obj = PyPDFForm(template_stream).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.stream)
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected

        for _, elements in template_core.get_elements_by_page(obj.read()).items():
            assert not elements


def test_register_bad_fonts():
    assert not PyPDFForm.register_font("foo", b"foo")
    assert not PyPDFForm.register_font("foo", "foo")


def test_fill_font_liberation_serif_italic(
    template_stream, pdf_samples, font_samples, data_dict, request
):
    with open(os.path.join(font_samples, "LiberationSerif-Italic.ttf"), "rb+") as _f:
        stream = _f.read()
        _f.seek(0)
        PyPDFForm.register_font("LiberationSerif-Italic", stream)

    expected_path = os.path.join(pdf_samples, "sample_filled_font_liberation_serif_italic.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PyPDFForm(template_stream, global_font="LiberationSerif-Italic").fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if isinstance(v, Text):
                assert v.font == "LiberationSerif-Italic"
                assert v.font_size == constants.GLOBAL_FONT_SIZE
                assert v.font_color == constants.GLOBAL_FONT_COLOR
                assert v.text_x_offset == constants.GLOBAL_TEXT_X_OFFSET
                assert v.text_y_offset == constants.GLOBAL_TEXT_Y_OFFSET
                assert v.text_wrap_length == constants.GLOBAL_TEXT_WRAP_LENGTH


def test_fill_font_20(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_font_20.pdf")
    with open(expected_path, "rb+") as f:
        obj = PyPDFForm(template_stream, global_font_size=20).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if isinstance(v, Text):
                assert v.font == constants.GLOBAL_FONT
                assert v.font_size == 20
                assert v.font_color == constants.GLOBAL_FONT_COLOR
                assert v.text_x_offset == constants.GLOBAL_TEXT_X_OFFSET
                assert v.text_y_offset == constants.GLOBAL_TEXT_Y_OFFSET
                assert v.text_wrap_length == constants.GLOBAL_TEXT_WRAP_LENGTH


def test_fill_font_color_red(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_font_color_red.pdf")
    with open(
        expected_path, "rb+"
    ) as f:
        obj = PyPDFForm(template_stream, global_font_color=(1, 0, 0)).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if isinstance(v, Text):
                assert v.font == constants.GLOBAL_FONT
                assert v.font_size == constants.GLOBAL_FONT_SIZE
                assert v.font_color == (1, 0, 0)
                assert v.text_x_offset == constants.GLOBAL_TEXT_X_OFFSET
                assert v.text_y_offset == constants.GLOBAL_TEXT_Y_OFFSET
                assert v.text_wrap_length == constants.GLOBAL_TEXT_WRAP_LENGTH


def test_fill_offset_100(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_offset_100.pdf")
    with open(expected_path, "rb+") as f:
        obj = PyPDFForm(
            template_stream,
            global_text_x_offset=100,
            global_text_y_offset=-100,
        ).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if isinstance(v, Text):
                assert v.font == constants.GLOBAL_FONT
                assert v.font_size == constants.GLOBAL_FONT_SIZE
                assert v.font_color == constants.GLOBAL_FONT_COLOR
                assert v.text_x_offset == 100
                assert v.text_y_offset == -100
                assert v.text_wrap_length == constants.GLOBAL_TEXT_WRAP_LENGTH


def test_fill_wrap_2(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_text_wrap_2.pdf")
    with open(expected_path, "rb+") as f:
        obj = PyPDFForm(template_stream, global_text_wrap_length=2).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.elements.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if isinstance(v, Text):
                assert v.font == constants.GLOBAL_FONT
                assert v.font_size == constants.GLOBAL_FONT_SIZE
                assert v.font_color == constants.GLOBAL_FONT_COLOR
                assert v.text_x_offset == constants.GLOBAL_TEXT_X_OFFSET
                assert v.text_y_offset == constants.GLOBAL_TEXT_Y_OFFSET
                assert v.text_wrap_length == 2


def test_fill_with_customized_elements(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_customized_elements.pdf")
    with open(
        expected_path, "rb+"
    ) as f:
        obj = PyPDFForm(template_stream)

        obj.elements["test"].font = "LiberationSerif-Italic"
        obj.elements["test"].font_size = 20
        obj.elements["test"].font_color = (1, 0, 0)
        obj.elements["test_2"].font_color = (0, 1, 0)
        obj.elements["test_2"].text_x_offset = 50
        obj.elements["test_2"].text_y_offset = -50
        obj.elements["test_2"].text_wrap_length = 1
        obj.elements["test_3"].text_wrap_length = 2

        obj.fill(data_dict)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

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


def test_fill_radiobutton(pdf_samples, template_with_radiobutton_stream, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_radiobutton.pdf")
    with open(expected_path, "rb+") as f:
        obj = PyPDFForm(template_with_radiobutton_stream).fill(
            {
                "radio_1": 0,
                "radio_2": 1,
                "radio_3": 2,
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_fill_sejda_and_read(sejda_template, pdf_samples, sejda_data, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_sejda.pdf")
    with open(expected_path, "rb+") as f:
        obj = PyPDFForm(sejda_template).fill(
            sejda_data,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.stream)
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_draw_text_on_one_page(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "sample_pdf_with_drawn_text.pdf")
    with open(expected_path, "rb+") as f:
        obj = PyPDFForm(template_stream).draw_text(
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

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_draw_text_on_one_page_different_font(
    template_stream, pdf_samples, font_samples, request
):
    with open(
        os.path.join(font_samples, "LiberationSerif-BoldItalic.ttf"), "rb+"
    ) as _f:
        PyPDFForm.register_font("LiberationSerif-BoldItalic", _f.read())

    expected_path = os.path.join(pdf_samples, "sample_pdf_with_drawn_text_different_font.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PyPDFForm(template_stream).draw_text(
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
        request.config.results["stream"] = obj.read()
        request.config.results["expected_path"] = expected_path

        expected = f.read()

        if os.name == "nt":
            assert len(obj.stream) == len(expected)
        else:
            expected_path = os.path.join(
                    pdf_samples, "sample_pdf_with_drawn_text_different_font_linux.pdf")
            request.config.results["expected_path"] = expected_path
            with open(
                os.path.join(
                    pdf_samples, "sample_pdf_with_drawn_text_different_font_linux.pdf"
                ),
                "rb+",
            ) as f_linux:
                expected = f_linux.read()
                assert len(obj.stream) == len(expected)
                assert obj.stream == expected


def test_draw_image_on_one_page(template_stream, image_samples, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "sample_pdf_with_image.pdf")
    with open(expected_path, "rb+") as f:
        with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as _f:
            obj = PyPDFForm(template_stream).draw_image(
                _f,
                2,
                100,
                100,
                400,
                225,
            )

        expected = f.read()

        if os.name == "nt":
            request.config.results["expected_path"] = expected_path
            request.config.results["stream"] = obj.read()
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected


def test_draw_png_image_on_one_page(template_stream, image_samples, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "sample_pdf_with_png_image.pdf")
    with open(expected_path, "rb+") as f:
        obj = PyPDFForm(template_stream).draw_image(
            os.path.join(image_samples, "sample_png_image.png"),
            2,
            100,
            100,
            400,
            225,
        )

        expected = f.read()

        if os.name == "nt":
            request.config.results["expected_path"] = expected_path
            request.config.results["stream"] = obj.read()
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected


def test_addition_operator_3_times(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "sample_added_3_copies.pdf")
    with open(expected_path, "rb+") as f:
        result = PyPDFForm()

        for _ in range(3):
            result += PyPDFForm(template_stream).fill(data_dict)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = result.read()

        expected = f.read()
        assert len(result.read()) == len(expected)
        assert result.read() == expected
        assert len((result + PyPDFForm()).read()) == len(result.read())
        assert (result + PyPDFForm()).read() == result.read()


def test_addition_operator_3_times_sejda(sejda_template, pdf_samples, sejda_data, request):
    expected_path = os.path.join(pdf_samples, "sample_added_3_copies_sejda.pdf")
    with open(expected_path, "rb+") as f:
        result = PyPDFForm()

        for _ in range(3):
            result += PyPDFForm(sejda_template).fill(sejda_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = result.read()

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
    schema = PyPDFForm(sample_template_with_comb_text_field).generate_schema()

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

    data["LastName"] = "XXXXXXXX"
    try:
        validate(instance=data, schema=schema)
        assert False
    except ValidationError:
        pass

    data["LastName"] = "XXXXXXX"
    data["Gender"] = 1
    validate(instance=data, schema=schema)

    data["Gender"] = 2
    try:
        validate(instance=data, schema=schema)
        assert False
    except ValidationError:
        pass


def test_fill_right_aligned(sample_template_with_right_aligned_text_field, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_right_aligned.pdf")
    with open(expected_path, "rb+") as f:
        obj = PyPDFForm(sample_template_with_right_aligned_text_field).fill(
            {
                "name": "Hans Mustermann",
                "fulladdress": "Musterstr. 12, 82903 Musterdorf, Musterland",
                "advisorname": "Karl Test",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.stream)
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected

        for _, elements in template_core.get_elements_by_page(obj.read()).items():
            assert not elements


def test_paragraph_y_coordinate(sample_template_with_paragraph, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_paragraph_y_coordinate.pdf")
    with open(expected_path, "rb+") as f:
        obj = PyPDFForm(sample_template_with_paragraph).fill(
            {"paragraph_1": "test paragraph"}
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.stream)
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected
