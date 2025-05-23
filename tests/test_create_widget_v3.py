# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_create_not_supported_type_not_working(template_stream):
    obj = PdfWrapper(template_stream)
    stream = obj.read()
    assert (
        obj.create_widget(
            "foo",
            "foo",
            1,
            100,
            100,
        ).read()
        == stream
    )


def test_create_checkbox_default(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_default.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
        )
        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_default_filled(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_default_filled.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_default_filled_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_default_filled_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_complex(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_complex.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            size=100,
            button_style="check",
            tick_color=(0, 1, 0),
            bg_color=(0, 0, 1),
            border_color=(1, 0, 0),
            border_width=5,
        )

        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_complex_fill(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_complex_fill.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            size=100,
            button_style="check",
            tick_color=(0, 1, 0),
            bg_color=(0, 0, 1),
            border_color=(1, 0, 0),
            border_width=5,
        )
        obj.fill(obj.sample_data)

        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_complex_fill_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_complex_fill_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            size=100,
            button_style="check",
            tick_color=(0, 1, 0),
            bg_color=(0, 0, 1),
            border_color=(1, 0, 0),
            border_width=5,
        )
        obj.fill(obj.sample_data, flatten=True)

        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_check_fill(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_check_fill.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            button_style="check",
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_check_fill_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_check_fill_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            button_style="check",
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_circle_fill(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_circle_fill.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            button_style="circle",
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_circle_fill_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_circle_fill_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            button_style="circle",
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_cross_fill(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_cross_fill.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            button_style="cross",
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_cross_fill_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_cross_fill_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            button_style="cross",
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_text_default(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_text_default.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "text",
            "foo",
            1,
            100,
            100,
        )
        assert obj.schema["properties"]["foo"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_text_alpha_bg_color(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_alpha_bg_color.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "text",
            "foo",
            1,
            100,
            100,
            bg_color=(0, 0, 1, 0),
        )
        assert obj.schema["properties"]["foo"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_text_align_center(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_text_align_center.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "text",
            "foo",
            1,
            100,
            100,
            alignment=1,
        )
        assert obj.schema["properties"]["foo"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_text_align_right(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_text_align_right.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "text",
            "foo",
            1,
            100,
            100,
            alignment=2,
        )
        assert obj.schema["properties"]["foo"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_text_align_multiline(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_align_multiline.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "text",
            "foo",
            1,
            100,
            100,
            multiline=True,
        )
        assert obj.schema["properties"]["foo"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_text_default_filled(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_default_filled.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "text",
            "foo",
            1,
            100,
            100,
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_text_default_filled_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_default_filled_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "text",
            "foo",
            1,
            100,
            100,
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_text_complex(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_text_complex.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "text",
            "foo",
            1,
            100,
            100,
            width=400,
            height=400,
            max_length=2,
            font="Arial",
            font_size=50,
            font_color=(1, 0.5, 1),
            bg_color=(0, 0, 1),
            border_color=(1, 0, 0),
            border_width=5,
        )
        assert obj.schema["properties"]["foo"]["type"] == "string"
        assert obj.schema["properties"]["foo"]["maxLength"] == 2

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_text_complex_filled(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_complex_filled.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "text",
            "foo",
            1,
            100,
            100,
            width=400,
            height=400,
            max_length=2,
            font="Arial",
            font_size=50,
            font_color=(1, 0.5, 1),
            bg_color=(0, 0, 1),
            border_color=(1, 0, 0),
            border_width=5,
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_text_complex_filled_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_complex_filled_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "text",
            "foo",
            1,
            100,
            100,
            width=400,
            height=400,
            max_length=2,
            font="Arial",
            font_size=50,
            font_color=(1, 0.5, 1),
            bg_color=(0, 0, 1),
            border_color=(1, 0, 0),
            border_width=5,
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_text_comb(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_text_comb.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "text",
            "foo",
            1,
            100,
            100,
            max_length=3,
            comb=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_persist_old_widgets_fill(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_persist_old_widgets_fill.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["test"].font_size = 30
        obj.widgets["test"].font_color = (0, 1, 0)
        obj.create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
        ).fill(obj.sample_data)
        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_persist_old_widgets_fill_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_persist_old_widgets_fill_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["test"].font_size = 30
        obj.widgets["test"].font_color = (0, 1, 0)
        obj.create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
        ).fill(obj.sample_data, flatten=True)
        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_widget_sejda_fill(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_widget_sejda_fill.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.fill(obj.sample_data).create_widget(
            widget_type="text",
            name="new_text_field_widget",
            page_number=1,
            x=72,
            y=730,
            width=120,
            height=40,
            max_length=6,
            font="Helvetica",
            font_size=20,
            font_color=(0, 0, 1),
        ).fill(obj.sample_data)
        assert obj.schema["properties"]["new_text_field_widget"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_widget_sejda_fill_flatten_before(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_widget_sejda_fill_flatten_before.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.fill(obj.sample_data, flatten=True).create_widget(
            widget_type="text",
            name="new_text_field_widget",
            page_number=1,
            x=72,
            y=730,
            width=120,
            height=40,
            max_length=6,
            font="Helvetica",
            font_size=20,
            font_color=(0, 0, 1),
        ).fill(obj.sample_data)
        assert obj.schema["properties"]["new_text_field_widget"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_widget_sejda_fill_flatten_after(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_widget_sejda_fill_flatten_after.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.fill(obj.sample_data).create_widget(
            widget_type="text",
            name="new_text_field_widget",
            page_number=1,
            x=72,
            y=730,
            width=120,
            height=40,
            max_length=6,
            font="Helvetica",
            font_size=20,
            font_color=(0, 0, 1),
        ).fill(obj.sample_data, flatten=True)
        assert obj.schema["properties"]["new_text_field_widget"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_widget_sejda_schema(sejda_template):
    obj = PdfWrapper(sejda_template)
    old_schema = obj.schema
    schema = (
        PdfWrapper(sejda_template)
        .create_widget(
            widget_type="text",
            name="new_text_field_widget",
            page_number=1,
            x=72,
            y=730,
            width=120,
            height=40,
            max_length=6,
            font="Times-Roman",
            font_size=20,
            font_color=(0, 0, 1),
        )
        .schema
    )

    assert schema["properties"]["new_text_field_widget"]
    assert len(schema["properties"]) == len(old_schema["properties"]) + 1


def test_create_dropdown(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_dropdown.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            widget_type="dropdown",
            name="new_dropdown_widget",
            page_number=1,
            x=57,
            y=700,
            options=[
                "foo",
                "bar",
                "foobar",
            ],
            width=120,
            height=40,
            font="Arial",
            font_size=15,
            font_color=(1, 0, 0),
            bg_color=(0, 0, 1),
            border_color=(1, 0, 0),
            border_width=5,
        )
        assert obj.schema["properties"]["new_dropdown_widget"]["type"] == "integer"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_cmyk_color(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_fill_cmyk_color.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(pdf_samples, "widget", "sample_template_with_cmyk_color.pdf")
        ).fill({"foo": "foo"})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_cmyk_color_flatten(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_fill_cmyk_color_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(pdf_samples, "widget", "sample_template_with_cmyk_color.pdf")
        ).fill({"foo": "foo"}, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_radio_default(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_radio_default.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "radio",
            "radio",
            2,
            [50, 100, 150],
            [50, 100, 150],
        )
        assert obj.schema["properties"]["radio"]["type"] == "integer"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_radio_default_filled(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_radio_default_filled.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "radio",
            "radio",
            2,
            [50, 100, 150],
            [50, 100, 150],
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_radio_default_filled_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_radio_default_filled_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "radio",
            "radio",
            2,
            [50, 100, 150],
            [50, 100, 150],
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_radio_complex(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_radio_complex.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "radio",
            "radio",
            2,
            [50, 100, 150],
            [50, 100, 150],
            size=50,
            button_style="check",
            shape="circle",
            tick_color=(0, 1, 0),
            bg_color=(0, 0, 1, 1),
            border_color=(1, 0, 0),
            border_width=5,
        )
        assert obj.schema["properties"]["radio"]["type"] == "integer"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_signature_default(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_signature_default.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "signature",
            "sig_1",
            1,
            100,
            100,
            width=410,
            height=100,
        )
        assert obj.schema["properties"]["sig_1"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
