# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from jsonschema import ValidationError, validate

from PyPDFForm import BlankPage, Fields, PdfWrapper, RawElements, Widgets
from PyPDFForm.constants import DA, UNIQUE_SUFFIX_LENGTH, T, V
from PyPDFForm.deprecation import deprecation_notice
from PyPDFForm.middleware.base import Widget
from PyPDFForm.template import get_widgets_by_page


def test_deprecation_warning():
    with pytest.warns(
        DeprecationWarning, match="foo will be deprecated soon. Use bar instead."
    ) as r:
        deprecation_notice(
            "foo",
            "bar",
        )


def test_base_schema_definition():
    assert Widget("foo").schema_definition == {}


def test_write(template_stream, pdf_samples):
    assert PdfWrapper(template_stream).write(
        os.path.join(pdf_samples, "sample_template.pdf")
    )


def test_write_io(template_stream):
    buff = BytesIO()
    PdfWrapper(template_stream).write(buff)
    buff.seek(0)

    assert buff.read() == template_stream


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


def test_fill_flatten_then_unflatten(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill_flatten_then_unflatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(data_dict, flatten=True)
        obj.widgets["test_2"].readonly = False
        obj.widgets["check_3"].readonly = False

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

    obj = PdfWrapper().register_font("foo", b"foo")
    assert "foo" not in obj.fonts


@pytest.mark.posix_only
def test_register_global_font_fill(
    template_stream, pdf_samples, sample_font_stream, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_register_global_font_fill.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            sample_font_stream,
        )
        assert "new_font" in obj.fonts
        for v in obj.widgets.values():
            if isinstance(v, Widgets.Text):
                v.font = "new_font"
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_register_global_font_fill_flatten(
    template_stream, pdf_samples, sample_font_stream, data_dict, request
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
            sample_font_stream,
        )
        for v in obj.widgets.values():
            if isinstance(v, Widgets.Text):
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


def test_fill_font_20(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill_font_20.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream)
        for v in obj.widgets.values():
            if isinstance(v, Widgets.Text):
                v.font_size = 20
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_font_20_flatten(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill_font_20_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream)
        for v in obj.widgets.values():
            if isinstance(v, Widgets.Text):
                v.font_size = 20
        obj.fill(
            data_dict,
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_font_color_red(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill_font_color_red.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream)
        for v in obj.widgets.values():
            if isinstance(v, Widgets.Text):
                v.font_color = (1, 0, 0)
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_font_color_red_flatten(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill_font_color_red_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream)
        for v in obj.widgets.values():
            if isinstance(v, Widgets.Text):
                v.font_color = (1, 0, 0)
        obj.fill(data_dict, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_fill_with_customized_widgets(
    template_stream, pdf_samples, sample_font_stream, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_with_customized_widgets.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            sample_font_stream,
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


@pytest.mark.posix_only
def test_fill_with_customized_widgets_flatten(
    template_stream, pdf_samples, sample_font_stream, data_dict, request
):
    expected_path = os.path.join(
        pdf_samples, "test_fill_with_customized_widgets_flatten.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            sample_font_stream,
        )
        obj.widgets["test"].font = "new_font"
        obj.widgets["test"].font_size = 20
        obj.widgets["test"].font_color = (1, 0, 0)
        obj.widgets["test_2"].font_color = (0, 1, 0)
        obj.fill(
            data_dict,
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_radiobutton(template_with_radiobutton_stream, pdf_samples, request):
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


def test_fill_radiobutton_flatten_then_unflatten(
    template_with_radiobutton_stream, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "test_fill_radiobutton_flatten_then_unflatten.pdf"
    )
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
        obj.widgets["radio_2"].readonly = False

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_sejda(sejda_template, pdf_samples, sejda_data, request):
    expected_path = os.path.join(pdf_samples, "test_fill_sejda.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sejda_template).fill(sejda_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_sejda_flatten(sejda_template, pdf_samples, sejda_data, request):
    expected_path = os.path.join(pdf_samples, "test_fill_sejda_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sejda_template).fill(
            sejda_data,
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_sejda_flatten_then_unflatten(
    sejda_template, pdf_samples, sejda_data, request
):
    expected_path = os.path.join(
        pdf_samples, "test_fill_sejda_flatten_then_unflatten.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sejda_template).fill(
            sejda_data,
            flatten=True,
        )
        obj.widgets["buyer_name"].readonly = False
        obj.widgets["at_future_date"].readonly = False
        obj.widgets["purchase_option"].readonly = False

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_text_on_one_page(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_text_on_one_page.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw(
            [
                RawElements.RawText(
                    "drawn_text",
                    1,
                    300,
                    225,
                    font_size=20,
                    font_color=(1, 0, 0),
                )
            ]
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_multiline_text_on_one_page(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "test_draw_multiline_text_on_one_page.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw(
            [
                RawElements.RawText(
                    "drawn_text\ndrawn_text\ndrawn_text",
                    1,
                    300,
                    225,
                    font_size=20,
                    font_color=(1, 0, 0),
                )
            ]
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
        obj = PdfWrapper(template_with_radiobutton_stream).draw(
            [
                RawElements.RawText(
                    "drawn_text",
                    1,
                    300,
                    225,
                    font_size=20,
                    font_color=(1, 0, 0),
                )
            ]
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_text_on_sejda_template(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_text_on_sejda_template.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template).draw(
            [
                RawElements.RawText(
                    "drawn_text",
                    1,
                    300,
                    225,
                    font_size=20,
                    font_color=(1, 0, 0),
                )
            ]
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
            obj = PdfWrapper(template_stream).draw(
                [
                    RawElements.RawImage(
                        _f,
                        2,
                        100,
                        100,
                        400,
                        225,
                    )
                ]
            )

        expected = f.read()

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
            obj = PdfWrapper(template_with_radiobutton_stream).draw(
                [
                    RawElements.RawImage(
                        _f,
                        2,
                        100,
                        100,
                        400,
                        225,
                    )
                ]
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
            obj = PdfWrapper(sejda_template).draw(
                [
                    RawElements.RawImage(
                        _f,
                        2,
                        100,
                        100,
                        400,
                        225,
                    )
                ]
            )

        expected = f.read()

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_draw_png_image_on_one_page(
    template_stream, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_draw_png_image_on_one_page.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw(
            [
                RawElements.RawImage(
                    os.path.join(image_samples, "sample_png_image.png"),
                    2,
                    100,
                    100,
                    400,
                    225,
                )
            ]
        )

        expected = f.read()

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_draw_transparent_png_image_on_one_page(
    template_stream, image_samples, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "test_draw_transparent_png_image_on_one_page.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw(
            [
                RawElements.RawImage(
                    os.path.join(image_samples, "sample_transparent_png.png"),
                    1,
                    100,
                    100,
                    400,
                    225,
                )
            ]
        )

        expected = f.read()

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_text_and_image(template_stream, image_samples, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_text_and_image.pdf")
    with open(expected_path, "rb+") as f:
        with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as _f:
            obj = PdfWrapper(template_stream).draw(
                [
                    RawElements.RawText(
                        "drawn_text", 1, 300, 225, font_size=20, font_color=(1, 0, 0)
                    ),
                    RawElements.RawImage(_f, 2, 100, 100, 400, 225, rotation=180),
                ]
            )

        expected = f.read()

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


def test_merge_preserve_font_and_data(template_stream, sample_font_stream):
    result = PdfWrapper()

    for i in range(10):
        obj = PdfWrapper(template_stream).register_font("new_font", sample_font_stream)
        obj.widgets["test"].font = "new_font"
        result += obj.fill({"test": f"test_{i}"})

    for page, widgets in get_widgets_by_page(result.read()).items():
        for widget in widgets:
            if widget[T] == "test":
                assert widget[V] == "test_0"
                assert widget[DA].startswith("/F1")
            elif widget[T].startswith("test-"):
                assert widget[V] == f"test_{page // 3}"
                assert widget[DA].startswith("/F1")


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


def test_fill_right_aligned(
    sample_template_with_right_aligned_text_field, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_right_aligned.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_right_aligned_text_field).fill(
            {
                "name": "Hans Mustermann",
                "fulladdress": "Musterstr. 12, 82903 Musterdorf, Musterland",
                "advisorname": "Karl Test",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_right_aligned_flatten(
    sample_template_with_right_aligned_text_field, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_right_aligned_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_right_aligned_text_field).fill(
            {
                "name": "Hans Mustermann",
                "fulladdress": "Musterstr. 12, 82903 Musterdorf, Musterland",
                "advisorname": "Karl Test",
            },
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_version(pdf_samples):
    versions = ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "2.0"]

    for version in versions:
        obj = PdfWrapper(os.path.join(pdf_samples, "versions", f"{version}.pdf"))
        assert obj.version == version
        assert obj.change_version("2.0").version == "2.0"

    obj = PdfWrapper(os.path.join(pdf_samples, "versions", "unknown.pdf"))
    assert obj.version is None


@pytest.mark.posix_only
def test_fill_font_color(sample_template_with_font_colors, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_fill_font_color.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_font_colors).fill(
            {
                "red_12": "red",
                "green_14": "green",
                "blue_16": "blue",
                "mixed_auto": "mixed",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_fill_font_color_flatten(
    sample_template_with_font_colors, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_font_color_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_font_colors).fill(
            {
                "red_12": "red",
                "green_14": "green",
                "blue_16": "blue",
                "mixed_auto": "mixed",
            },
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_fill_complex_fonts(sample_template_with_complex_fonts, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_fill_complex_fonts.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_complex_fonts).fill(
            {
                "Courier": "Test",
                "Courier-Bold": "Test",
                "Courier-BoldOblique": "Test",
                "Courier-Oblique": "Test",
                "Helvetica": "Test",
                "Helvetica-Bold": "Test",
                "Helvetica-BoldOblique": "Test",
                "Helvetica-Oblique": "Test",
                "Times-Bold": "Test",
                "Times-BoldItalic": "Test",
                "Times-Italic": "Test",
                "Times-Roman": "Test",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_fill_complex_fonts_flatten(
    sample_template_with_complex_fonts, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_complex_fonts_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_complex_fonts).fill(
            {
                "Courier": "Test",
                "Courier-Bold": "Test",
                "Courier-BoldOblique": "Test",
                "Courier-Oblique": "Test",
                "Helvetica": "Test",
                "Helvetica-Bold": "Test",
                "Helvetica-BoldOblique": "Test",
                "Helvetica-Oblique": "Test",
                "Times-Bold": "Test",
                "Times-BoldItalic": "Test",
                "Times-Italic": "Test",
                "Times-Roman": "Test",
            },
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_pages(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_pages.pdf")
    obj = PdfWrapper(template_stream)

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[0].read()
        assert obj.pages[0].read() == f.read()


@pytest.mark.posix_only
def test_pages_preserve_font(template_stream, pdf_samples, sample_font_stream, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_pages_preserve_font.pdf")
    obj = PdfWrapper(template_stream)
    obj.register_font("new_font", sample_font_stream)
    obj.widgets["test_2"].font = "new_font"

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[1].read()
        assert obj.pages[1].read() == f.read()


def test_sejda_pages_1(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_sejda_pages_1.pdf")
    obj = PdfWrapper(sejda_template)

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[0].read()
        assert obj.pages[0].read() == f.read()


def test_sejda_pages_2(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_sejda_pages_2.pdf")
    obj = PdfWrapper(sejda_template)

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[1].read()
        assert obj.pages[1].read() == f.read()


def test_radio_pages_1(template_with_radiobutton_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_radio_pages_1.pdf")
    obj = PdfWrapper(template_with_radiobutton_stream)

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[0].read()
        assert obj.pages[0].read() == f.read()


def test_radio_pages_2(template_with_radiobutton_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_radio_pages_2.pdf")
    obj = PdfWrapper(template_with_radiobutton_stream)

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[1].read()
        assert obj.pages[1].read() == f.read()


def test_radio_pages_3(template_with_radiobutton_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_radio_pages_3.pdf")
    obj = PdfWrapper(template_with_radiobutton_stream)

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[2].read()
        assert obj.pages[2].read() == f.read()


def test_pages_inherit_attributes(template_stream):
    obj = PdfWrapper(
        template_stream,
        use_full_widget_name=True,
    )

    for page in obj.pages:
        assert getattr(page, "use_full_widget_name")


def test_generate_coordinate_grid(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_generate_coordinate_grid.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).generate_coordinate_grid((1, 0, 1))

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_generate_coordinate_grid_margin_50(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "test_generate_coordinate_grid_margin_50.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).generate_coordinate_grid((1, 0, 1), margin=50)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_checkbox_change_size(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_checkbox_change_size.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["check"].size = 50
        obj.widgets["check_2"].size = 40
        obj.widgets["check_3"].size = 60

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_radio_change_size(template_with_radiobutton_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_radio_change_size.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_with_radiobutton_stream)
        obj.widgets["radio_1"].size = 50
        obj.widgets["radio_2"].size = 40
        obj.widgets["radio_3"].size = 60

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_image(
    sample_template_with_image_field, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_image.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_image_field).fill(
            {"image_1": os.path.join(image_samples, "sample_image.jpg")},
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_image_flatten(
    sample_template_with_image_field, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_image_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_image_field).fill(
            {"image_1": os.path.join(image_samples, "sample_image.jpg")},
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_update_radio_key(template_with_radiobutton_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_update_radio_key.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_with_radiobutton_stream)
        obj.update_widget_key("radio_3", "RADIO")
        obj.fill({"RADIO": 0})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_update_sejda_key(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_update_sejda_key.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.update_widget_key("year", "YEAR")
        obj.update_widget_key("at_future_date", "FUTURE_DATE")
        obj.update_widget_key("purchase_option", "PURCHASE_OPTION")
        obj.update_widget_key("buyer_signed_date", "BUYER_SIGNED_DATE")
        obj.fill(
            {
                "YEAR": "12",
                "FUTURE_DATE": True,
                "PURCHASE_OPTION": 1,
                "BUYER_SIGNED_DATE": "2012-01-01",
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_uncheck_checkbox(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_uncheck_checkbox.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(os.path.join(pdf_samples, "sample_template_filled.pdf")).fill(
            {"check": False, "check_2": False, "check_3": False},
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_uncheck_checkbox_flatten(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_uncheck_checkbox_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(os.path.join(pdf_samples, "sample_template_filled.pdf")).fill(
            {"check": False, "check_2": False, "check_3": False},
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_blank_page(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_blank_page.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(BlankPage() * 1)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        request.config.results["skip_regenerate"] = len(obj.read()) == len(expected)


@pytest.mark.posix_only
def test_blank_page_custom_size_multiply(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "test_blank_page_custom_size_multiply.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(BlankPage(595.35, 841.995) * 3)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        request.config.results["skip_regenerate"] = len(obj.read()) == len(expected)


def test_widget_coord_resolution():
    obj = PdfWrapper(BlankPage()).bulk_create_fields(
        [
            Fields.TextField("text", 1, 50, 100, width=200, height=150),
            Fields.CheckBoxField("check", 1, 150, 200, size=60),
            Fields.RadioGroup("radio", 1, [400, 500, 600], [450, 550, 650], size=10),
            Fields.DropdownField(
                "dropdown", 1, 400, 100, width=250, height=200, options=["foo", "bar"]
            ),
            Fields.ImageField("image", 1, 300, 400, width=400, height=300),
            Fields.SignatureField("signature", 1, 500, 600, width=600, height=500),
        ]
    )

    assert obj.widgets["text"].x == 50
    assert obj.widgets["text"].y == 100
    assert obj.widgets["text"].width == 200
    assert obj.widgets["text"].height == 150

    assert obj.widgets["check"].x == 150
    assert obj.widgets["check"].y == 200
    assert obj.widgets["check"].width == 60
    assert obj.widgets["check"].height == 60

    assert obj.widgets["radio"].x == [400, 500, 600]
    assert obj.widgets["radio"].y == [450, 550, 650]
    assert obj.widgets["radio"].width == 10
    assert obj.widgets["radio"].height == 10

    assert obj.widgets["dropdown"].x == 400
    assert obj.widgets["dropdown"].y == 100
    assert obj.widgets["dropdown"].width == 250
    assert obj.widgets["dropdown"].height == 200

    assert obj.widgets["image"].x == 300
    assert obj.widgets["image"].y == 400
    assert obj.widgets["image"].width == 400
    assert obj.widgets["image"].height == 300

    assert obj.widgets["signature"].x == 500
    assert obj.widgets["signature"].y == 600
    assert obj.widgets["signature"].width == 600
    assert obj.widgets["signature"].height == 500
