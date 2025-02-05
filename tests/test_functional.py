# -*- coding: utf-8 -*-

import os

from jsonschema import ValidationError, validate

from PyPDFForm import PdfWrapper, constants, template
from PyPDFForm.middleware.base import Widget
from PyPDFForm.middleware.text import Text


def test_base_schema_definition():
    assert Widget("foo").schema_definition == {}


def test_fill(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "sample_filled.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.stream)
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected

        for widgets in template.get_widgets_by_page(obj.read()).values():
            assert not widgets


def test_register_bad_fonts():
    assert not PdfWrapper.register_font("foo", b"foo")
    assert not PdfWrapper.register_font("foo", "foo")


def test_fill_font_liberation_serif_italic(
    template_stream, pdf_samples, font_samples, data_dict, request
):
    with open(os.path.join(font_samples, "LiberationSerif-Italic.ttf"), "rb+") as _f:
        stream = _f.read()
        _f.seek(0)
        PdfWrapper.register_font("LiberationSerif-Italic", stream)

    expected_path = os.path.join(
        pdf_samples, "sample_filled_font_liberation_serif_italic.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream, global_font="LiberationSerif-Italic").fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.widgets.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if isinstance(v, Text):
                assert v.font == "LiberationSerif-Italic"
                assert v.font_color == constants.DEFAULT_FONT_COLOR


def test_fill_font_20(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_font_20.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream, global_font_size=20).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.widgets.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if isinstance(v, Text):
                assert v.font == constants.DEFAULT_FONT
                assert v.font_size == 20
                assert v.font_color == constants.DEFAULT_FONT_COLOR


def test_fill_font_color_red(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_font_color_red.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream, global_font_color=(1, 0, 0)).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.widgets.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if isinstance(v, Text):
                assert v.font == constants.DEFAULT_FONT
                assert v.font_color == (1, 0, 0)


def test_fill_with_customized_widgets(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_customized_widgets.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)

        obj.widgets["test"].font = "LiberationSerif-Italic"
        obj.widgets["test"].font_size = 20
        obj.widgets["test"].font_color = (1, 0, 0)
        obj.widgets["test_2"].font_color = (0, 1, 0)

        obj.fill(data_dict)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected

        for k, v in obj.widgets.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

        assert obj.widgets["test"].font == "LiberationSerif-Italic"
        assert obj.widgets["test"].font_size == 20
        assert obj.widgets["test"].font_color == (1, 0, 0)
        assert obj.widgets["test_2"].font_color == (0, 1, 0)


def test_fill_radiobutton(pdf_samples, template_with_radiobutton_stream, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_radiobutton.pdf")
    with open(expected_path, "rb+") as f:
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
        assert obj.stream == expected


def test_fill_sejda_and_read(sejda_template, pdf_samples, sejda_data, request):
    expected_path = os.path.join(pdf_samples, "sample_filled_sejda.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template).fill(
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
        obj = PdfWrapper(template_stream).draw_text(
            "drawn_text",
            1,
            300,
            225,
            font=constants.DEFAULT_FONT,
            font_size=20,
            font_color=(1, 0, 0),
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_draw_text_new_line_symbol(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "sample_pdf_with_drawn_text_new_line_symbol.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw_text(
            "test\ntest\ntest",
            1,
            300,
            225,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_draw_image_on_one_page(template_stream, image_samples, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "sample_pdf_with_image.pdf")
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
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected


def test_draw_png_image_on_one_page(
    template_stream, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "sample_pdf_with_png_image.pdf")
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
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected


def test_draw_transparent_png_image_on_one_page(
    template_stream, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "sample_pdf_with_transparent_png.pdf")
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
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected


def test_addition_operator_3_times(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "sample_added_3_copies.pdf")
    with open(expected_path, "rb+") as f:
        result = PdfWrapper()

        for _ in range(3):
            result += PdfWrapper(template_stream).fill(data_dict)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = result.read()

        expected = f.read()
        assert len(result.read()) == len(expected)
        assert result.read() == expected
        assert len((result + PdfWrapper()).read()) == len(result.read())
        assert (result + PdfWrapper()).read() == result.read()


def test_addition_operator_3_times_sejda(
    sejda_template, pdf_samples, sejda_data, request
):
    expected_path = os.path.join(pdf_samples, "sample_added_3_copies_sejda.pdf")
    with open(expected_path, "rb+") as f:
        result = PdfWrapper()

        for _ in range(3):
            result += PdfWrapper(sejda_template).fill(sejda_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = result.read()

        expected = f.read()
        assert len(result.read()) == len(expected)
        assert result.read() == expected


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
    expected_path = os.path.join(pdf_samples, "sample_filled_right_aligned.pdf")
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
        assert len(obj.read()) == len(obj.stream)
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected

        for widgets in template.get_widgets_by_page(obj.read()).values():
            assert not widgets


def test_version(pdf_samples):
    versions = ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "2.0"]

    for version in versions:
        obj = PdfWrapper(os.path.join(pdf_samples, "versions", f"{version}.pdf"))
        assert obj.version == version
        assert obj.change_version("2.0").version == "2.0"

    obj = PdfWrapper(os.path.join(pdf_samples, "versions", "unknown.pdf"))
    assert obj.version is None


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
        assert len(obj.read()) == len(obj.stream)
        assert obj.read() == obj.stream

        expected = f.read()

        if os.name != "nt":
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected


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

        if os.name != "nt":
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected


def test_pages(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "pages", "sample_template_page_1.pdf")
    obj = PdfWrapper(template_stream)

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[0].read()
        assert obj.pages[0].read() == f.read()


def test_pages_inherit_attributes(template_stream):
    obj = PdfWrapper(
        template_stream,
        global_font="Courier",
        global_font_size=20,
        global_font_color=(1, 0, 0),
        use_full_widget_name=True,
    )

    for page in obj.pages:
        assert getattr(page, "global_font") == "Courier"
        assert getattr(page, "global_font_size") == 20
        assert getattr(page, "global_font_color") == (1, 0, 0)
        assert getattr(page, "use_full_widget_name")


def test_generate_coordinate_grid(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_generate_coordinate_grid.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).generate_coordinate_grid((1, 0, 1))

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


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
        assert obj.stream == expected


def test_checkbox_change_size_and_button_style(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "test_checkbox_change_size_and_button_style.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["check"].size = 50
        obj.widgets["check"].button_style = "cross"
        obj.widgets["check_2"].size = 40
        obj.widgets["check_2"].button_style = "circle"
        obj.widgets["check_3"].size = 60
        obj.widgets["check_3"].button_style = "check"
        obj = obj.fill(
            {
                "check": True,
                "check_2": True,
                "check_3": True,
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_radio_change_size_and_button_style(
    template_with_radiobutton_stream, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "test_radio_change_size_and_button_style.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_with_radiobutton_stream)
        obj.widgets["radio_1"].size = 50
        obj.widgets["radio_1"].button_style = "cross"
        obj.widgets["radio_2"].size = 40
        obj.widgets["radio_2"].button_style = "circle"
        obj.widgets["radio_3"].size = 60
        obj.widgets["radio_3"].button_style = "check"
        obj = obj.fill(
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


def test_fill_image(
    sample_template_with_image_field, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "sample_filled_image.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_image_field).fill(
            {"image_1": os.path.join(image_samples, "sample_image.jpg")},
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_update_radio_key(template_with_radiobutton_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_update_radio_key.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_with_radiobutton_stream)
        obj.update_widget_key("radio_3", "RADIO")

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.preview

        expected = f.read()

        assert len(obj.preview) == len(expected)
        assert obj.preview == expected


def test_update_sejda_key(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_update_sejda_key.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.update_widget_key("year", "YEAR")
        obj.update_widget_key("at_future_date", "FUTURE_DATE")
        obj.update_widget_key("purchase_option", "PURCHASE_OPTION")
        obj.update_widget_key("buyer_signed_date", "BUYER_SIGNED_DATE")

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.preview

        expected = f.read()

        assert len(obj.preview) == len(expected)
        assert obj.preview == expected
