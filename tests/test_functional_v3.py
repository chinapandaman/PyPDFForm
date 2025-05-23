# -*- coding: utf-8 -*-

import os

from jsonschema import ValidationError, validate

from PyPDFForm import PdfWrapper
from PyPDFForm.template import get_widgets_by_page
from PyPDFForm.constants import UNIQUE_SUFFIX_LENGTH, T, V
from PyPDFForm.middleware.base import Widget
from PyPDFForm.middleware.text import Text


def test_base_schema_definition():
    assert Widget("foo").schema_definition == {}


def test_fill(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.read())
        assert obj.read() == obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_flatten(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(data_dict, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.read())
        assert obj.read() == obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_register_bad_fonts():
    assert not PdfWrapper().register_font("foo", b"foo").read()
    assert not PdfWrapper().register_font("foo", "foo").read()


def test_register_global_font_fill(
    template_stream, pdf_samples, samle_font_stream, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_register_global_font_fill.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            samle_font_stream,
        )
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font = "new_font"
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_register_global_font_fill_flatten(
    template_stream, pdf_samples, samle_font_stream, data_dict, request
):
    expected_path = os.path.join(
        pdf_samples, "test_register_global_font_fill_flatten.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            samle_font_stream,
        )
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font = "new_font"
        obj.fill(
            data_dict,
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_font_20(
    template_stream, pdf_samples, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_font_20.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream)
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font_size = 20
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_font_20_flatten(
    template_stream, pdf_samples, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_font_20_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream)
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font_size = 20
        obj.fill(
            data_dict, flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_font_color_red(
    template_stream, pdf_samples, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_font_color_red.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream)
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font_color = (1, 0, 0)
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_font_color_red_flatten(
    template_stream, pdf_samples, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_font_color_red_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream)
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font_color = (1, 0, 0)
        obj.fill(
            data_dict, flatten=True
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_with_customized_widgets(
    template_stream, pdf_samples, samle_font_stream, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_with_customized_widgets.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            samle_font_stream,
        )
        obj.widgets["test"].font = "new_font"
        obj.widgets["test"].font_size = 20
        obj.widgets["test"].font_color = (1, 0, 0)
        obj.widgets["test_2"].font_color = (0, 1, 0)
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_with_customized_widgets_flatten(
    template_stream, pdf_samples, samle_font_stream, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_with_customized_widgets_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            samle_font_stream,
        )
        obj.widgets["test"].font = "new_font"
        obj.widgets["test"].font_size = 20
        obj.widgets["test"].font_color = (1, 0, 0)
        obj.widgets["test_2"].font_color = (0, 1, 0)
        obj.fill(
            data_dict, flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_radiobutton(
    template_with_radiobutton_stream, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_radiobutton.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_with_radiobutton_stream).fill(
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
        assert obj.read() == expected


def test_fill_radiobutton_flatten(
    template_with_radiobutton_stream, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_radiobutton_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_with_radiobutton_stream).fill(
            {
                "radio_1": 0,
                "radio_2": 1,
                "radio_3": 2,
            },
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_sejda(
    sejda_template, pdf_samples, sejda_data, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_sejda.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sejda_template).fill(
            sejda_data
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_sejda_flatten(
    sejda_template, pdf_samples, sejda_data, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_sejda_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sejda_template).fill(
            sejda_data, flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_text_on_one_page(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_text_on_one_page.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw_text(
            "drawn_text",
            1,
            300,
            225,
            font_size=20,
            font_color=(1, 0, 0),
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_text_on_radio_template(
    template_with_radiobutton_stream, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_draw_text_on_radio_template.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_with_radiobutton_stream).draw_text(
            "drawn_text",
            1,
            300,
            225,
            font_size=20,
            font_color=(1, 0, 0),
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_text_on_sejda_template(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_text_on_sejda_template.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template).draw_text(
            "drawn_text",
            1,
            300,
            225,
            font_size=20,
            font_color=(1, 0, 0),
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_image_on_one_page(template_stream, image_samples, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_image_on_one_page.pdf")
    with open(expected_path, "rb+") as f:
        with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as _f:
            obj = PdfWrapper(template_stream).draw_image(
                _f,
                2,
                100,
                100,
                400,
                225,
            )

        expected = f.read()

        if os.name != "nt":
            request.config.results["expected_path"] = expected_path
            request.config.results["stream"] = obj.read()
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected


def test_draw_image_on_radio_template(
    template_with_radiobutton_stream, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_draw_image_on_radio_template.pdf")
    with open(expected_path, "rb+") as f:
        with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as _f:
            obj = PdfWrapper(template_with_radiobutton_stream).draw_image(
                _f,
                2,
                100,
                100,
                400,
                225,
            )

        expected = f.read()

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_image_on_sejda_template(
    sejda_template, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_draw_image_on_sejda_template.pdf")
    with open(expected_path, "rb+") as f:
        with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as _f:
            obj = PdfWrapper(sejda_template).draw_image(
                _f,
                2,
                100,
                100,
                400,
                225,
            )

        expected = f.read()

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_png_image_on_one_page(
    template_stream, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_draw_png_image_on_one_page.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw_image(
            os.path.join(image_samples, "sample_png_image.png"),
            2,
            100,
            100,
            400,
            225,
        )

        expected = f.read()

        if os.name != "nt":
            request.config.results["expected_path"] = expected_path
            request.config.results["stream"] = obj.read()
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected


def test_draw_transparent_png_image_on_one_page(
    template_stream, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_draw_transparent_png_image_on_one_page.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw_image(
            os.path.join(image_samples, "sample_transparent_png.png"),
            1,
            100,
            100,
            400,
            225,
        )

        expected = f.read()

        if os.name != "nt":
            request.config.results["expected_path"] = expected_path
            request.config.results["stream"] = obj.read()
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected


def test_addition_operator_3_times(template_stream, data_dict):
    result = PdfWrapper()

    for _ in range(3):
        result += PdfWrapper(template_stream).fill(data_dict)

    assert len((result + PdfWrapper()).read()) == len(result.read())
    assert (result + PdfWrapper()).read() == result.read()
    assert len(result.pages) == len(PdfWrapper(template_stream).pages) * 3


def test_merging_unique_suffix(template_stream):
    result = PdfWrapper()

    for i in range(10):
        obj = PdfWrapper(
            PdfWrapper(template_stream).fill({"test": f"value-{i}"}).read()
        )
        result += obj

    merged = PdfWrapper(result.read())

    for page, widgets in get_widgets_by_page(result.read()).items():
        for widget in widgets:
            assert widget[T] in merged.widgets
            if widget[T] == "test":
                assert widget[V] == "value-0"
            elif V in widget and "value-" in widget[V]:
                assert widget[V] == f"value-{page // 3}"
                assert widget[T].split("-")[0] == "test"
                assert len(widget[T].split("-")[1]) == UNIQUE_SUFFIX_LENGTH


def test_schema(sample_template_with_comb_text_field):
    data = {
        "FirstName": "John",
        "MiddleName": "Joe",
        "LastName": "XXXXXXX",
        "Awesomeness": True,
        "Gender": 0,
    }
    schema = PdfWrapper(sample_template_with_comb_text_field).schema

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
        raise AssertionError
    except ValidationError:
        pass

    data["LastName"] = "XXXXXXX"
    data["Gender"] = 1
    validate(instance=data, schema=schema)

    data["Gender"] = 2
    try:
        validate(instance=data, schema=schema)
        raise AssertionError
    except ValidationError:
        pass


def test_sample_data(sejda_template_complex):
    obj = PdfWrapper(sejda_template_complex)
    try:
        validate(instance=obj.sample_data, schema=obj.schema)
    except ValidationError:
        raise AssertionError from ValidationError

    widget = Widget("foo")
    try:
        widget.sample_value()
        raise AssertionError
    except NotImplementedError:
        pass


def test_sample_data_max_boundary(sample_template_with_comb_text_field):
    obj = PdfWrapper(sample_template_with_comb_text_field)
    try:
        validate(instance=obj.sample_data, schema=obj.schema)
    except ValidationError:
        raise AssertionError from ValidationError

    assert obj.sample_data["LastName"] == "LastNam"
    assert obj.sample_data["Gender"] == 1
