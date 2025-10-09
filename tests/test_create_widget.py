# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import Fields, PdfWrapper


def test_create_not_supported_type_not_working(template_stream):
    obj = PdfWrapper(template_stream)
    stream = obj.read()

    with pytest.warns(DeprecationWarning) as r:  # noqa: PT030, PT031
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
        assert r


@pytest.mark.posix_only
def test_create_checkbox_default(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_default.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
            )
        )
        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_default_filled(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_default_filled.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
            )
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_default_filled_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_default_filled_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
            )
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_complex(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_complex.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                size=100,
                button_style="check",
                tick_color=(0, 1, 0),
                bg_color=(0, 0, 1),
                border_color=(1, 0, 0),
                border_width=5,
            )
        )

        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_complex_fill(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_complex_fill.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                size=100,
                button_style="check",
                tick_color=(0, 1, 0),
                bg_color=(0, 0, 1),
                border_color=(1, 0, 0),
                border_width=5,
            )
        )
        obj.fill(obj.sample_data)

        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_complex_fill_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_complex_fill_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                size=100,
                button_style="check",
                tick_color=(0, 1, 0),
                bg_color=(0, 0, 1),
                border_color=(1, 0, 0),
                border_width=5,
            )
        )
        obj.fill(obj.sample_data, flatten=True)

        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_check_fill(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_check_fill.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                button_style="check",
            )
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_check_fill_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_check_fill_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                button_style="check",
            )
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_circle_fill(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_circle_fill.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                button_style="circle",
            )
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_circle_fill_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_circle_fill_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                button_style="circle",
            )
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_cross_fill(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_cross_fill.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                button_style="cross",
            )
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_cross_fill_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_cross_fill_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                button_style="cross",
            )
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_text_default(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_text_default.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.TextField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
            )
        )
        assert obj.schema["properties"]["foo"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_text_alpha_bg_color(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_alpha_bg_color.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.TextField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                bg_color=(0, 0, 1, 0),
            )
        )
        assert obj.schema["properties"]["foo"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_text_align_center(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_align_center.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.TextField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                alignment=1,
            )
        )
        assert obj.schema["properties"]["foo"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_text_align_right(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_align_right.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.TextField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                alignment=2,
            )
        )
        assert obj.schema["properties"]["foo"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_text_multiline(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_align_multiline.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.TextField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                multiline=True,
            )
        )
        assert obj.schema["properties"]["foo"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_text_default_filled(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_default_filled.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.TextField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
            )
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_text_default_filled_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_default_filled_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.TextField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
            )
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_text_complex(template_stream, pdf_samples, sample_font_stream, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_text_complex.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(template_stream)
            .register_font("new_font", sample_font_stream)
            .create_field(
                Fields.TextField(
                    name="foo",
                    page_number=1,
                    x=100,
                    y=100,
                    width=400,
                    height=400,
                    max_length=2,
                    font="new_font",
                    font_size=50,
                    font_color=(1, 0.5, 1),
                    bg_color=(0, 0, 1),
                    border_color=(1, 0, 0),
                    border_width=5,
                )
            )
        )
        assert obj.schema["properties"]["foo"]["type"] == "string"
        assert obj.schema["properties"]["foo"]["maxLength"] == 2

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_text_complex_filled(
    template_stream, pdf_samples, sample_font_stream, request
):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_complex_filled.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(template_stream)
            .register_font("new_font", sample_font_stream)
            .create_field(
                Fields.TextField(
                    name="foo",
                    page_number=1,
                    x=100,
                    y=100,
                    width=400,
                    height=400,
                    max_length=2,
                    font="new_font",
                    font_size=50,
                    font_color=(1, 0.5, 1),
                    bg_color=(0, 0, 1),
                    border_color=(1, 0, 0),
                    border_width=5,
                )
            )
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_text_complex_filled_flatten(
    template_stream, pdf_samples, sample_font_stream, request
):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_complex_filled_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(template_stream)
            .register_font("new_font", sample_font_stream)
            .create_field(
                Fields.TextField(
                    name="foo",
                    page_number=1,
                    x=100,
                    y=100,
                    width=400,
                    height=400,
                    max_length=2,
                    font="new_font",
                    font_size=50,
                    font_color=(1, 0.5, 1),
                    bg_color=(0, 0, 1),
                    border_color=(1, 0, 0),
                    border_width=5,
                )
            )
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_text_comb(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_text_comb.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.TextField(
                "foo",
                page_number=1,
                x=100,
                y=100,
                max_length=3,
                comb=True,
            )
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_persist_old_widgets_fill(
    template_stream, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_persist_old_widgets_fill.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["test"].font_size = 30
        obj.widgets["test"].font_color = (0, 1, 0)
        obj.create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
            )
        ).fill(obj.sample_data)
        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_checkbox_persist_old_widgets_fill_flatten(
    template_stream, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples,
        "widget",
        "test_create_checkbox_persist_old_widgets_fill_flatten.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["test"].font_size = 30
        obj.widgets["test"].font_color = (0, 1, 0)
        obj.create_field(
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
            )
        ).fill(obj.sample_data, flatten=True)
        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_widget_sejda_fill(sejda_template, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_widget_sejda_fill.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.fill(obj.sample_data).create_field(
            Fields.TextField(
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
            )
        ).fill(obj.sample_data)
        assert obj.schema["properties"]["new_text_field_widget"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_widget_sejda_fill_flatten_before(sejda_template, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_widget_sejda_fill_flatten_before.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.fill(obj.sample_data, flatten=True).create_field(
            Fields.TextField(
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
            )
        ).fill(obj.sample_data)
        assert obj.schema["properties"]["new_text_field_widget"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_widget_sejda_fill_flatten_after(sejda_template, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_widget_sejda_fill_flatten_after.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.fill(obj.sample_data).create_field(
            Fields.TextField(
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
            )
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
        .create_field(
            Fields.TextField(
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
        )
        .schema
    )

    assert schema["properties"]["new_text_field_widget"]
    assert len(schema["properties"]) == len(old_schema["properties"]) + 1


@pytest.mark.posix_only
def test_create_dropdown(template_stream, pdf_samples, sample_font_stream, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_dropdown.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(template_stream)
            .register_font("new_font", sample_font_stream)
            .create_field(
                Fields.DropdownField(
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
                    font="new_font",
                    font_size=15,
                    font_color=(1, 0, 0),
                    bg_color=(0, 0, 1),
                    border_color=(1, 0, 0),
                    border_width=5,
                )
            )
        )
        assert obj.schema["properties"]["new_dropdown_widget"]["type"] == "integer"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_dropdown_with_export_values(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_dropdown_with_export_values.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.DropdownField(
                name="new_dropdown_widget",
                page_number=1,
                x=57,
                y=700,
                options=[
                    ("foo", "foo_export"),
                    ("bar", "bar_export"),
                    ("foobar", "foobar_export"),
                ],
            )
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
    expected_path = os.path.join(
        pdf_samples, "widget", "test_fill_cmyk_color_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(pdf_samples, "widget", "sample_template_with_cmyk_color.pdf")
        ).fill({"foo": "foo"}, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_radio_default(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_radio_default.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.RadioGroup(
                name="radio",
                page_number=2,
                x=[50, 100, 150],
                y=[50, 100, 150],
            )
        )
        assert obj.schema["properties"]["radio"]["type"] == "integer"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_radio_default_filled(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_radio_default_filled.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.RadioGroup(
                name="radio",
                page_number=2,
                x=[50, 100, 150],
                y=[50, 100, 150],
            )
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_radio_default_filled_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_radio_default_filled_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.RadioGroup(
                name="radio",
                page_number=2,
                x=[50, 100, 150],
                y=[50, 100, 150],
            )
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_radio_complex(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_radio_complex.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.RadioGroup(
                name="radio",
                page_number=2,
                x=[50, 100, 150],
                y=[50, 100, 150],
                size=50,
                button_style="check",
                shape="circle",
                tick_color=(0, 1, 0),
                bg_color=(0, 0, 1, 1),
                border_color=(1, 0, 0),
                border_width=5,
            )
        )
        assert obj.schema["properties"]["radio"]["type"] == "integer"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_signature_default(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_signature_default.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.SignatureField(
                name="sig_1",
                page_number=1,
                x=100,
                y=100,
                width=410,
                height=100,
            )
        )
        assert obj.schema["properties"]["sig_1"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_signature_default_filled(
    template_stream, pdf_samples, image_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_signature_default_filled.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(template_stream)
            .create_field(
                Fields.SignatureField(
                    name="sig_1",
                    page_number=1,
                    x=100,
                    y=100,
                    width=410,
                    height=100,
                )
            )
            .fill({"sig_1": os.path.join(image_samples, "sample_signature.png")})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_signature_default_filled_flatten(
    template_stream, pdf_samples, image_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_signature_default_filled_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(template_stream)
            .create_field(
                Fields.SignatureField(
                    name="sig_1",
                    page_number=1,
                    x=100,
                    y=100,
                    width=410,
                    height=100,
                )
            )
            .fill(
                {"sig_1": os.path.join(image_samples, "sample_signature.png")},
                flatten=True,
            )
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_image_default(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_image_default.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_field(
            Fields.ImageField(
                name="image_1",
                page_number=1,
                x=100,
                y=100,
                width=192,
                height=108,
            )
        )
        assert obj.schema["properties"]["image_1"]["type"] == "string"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_image_default_filled(
    template_stream, pdf_samples, image_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_image_default_filled.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(template_stream)
            .create_field(
                Fields.ImageField(
                    name="image_1",
                    page_number=1,
                    x=100,
                    y=100,
                    width=192,
                    height=108,
                )
            )
            .fill({"image_1": os.path.join(image_samples, "sample_image.jpg")})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_image_default_filled_flatten(
    template_stream, pdf_samples, image_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_image_default_filled_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(template_stream)
            .create_field(
                Fields.ImageField(
                    name="image_1",
                    page_number=1,
                    x=100,
                    y=100,
                    width=192,
                    height=108,
                )
            )
            .fill(
                {"image_1": os.path.join(image_samples, "sample_image.jpg")},
                flatten=True,
            )
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_required_fields(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_required_fields.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(
                Fields.TextField(
                    name="new_text", page_number=1, x=100, y=100, required=True
                )
            )
            .create_field(
                Fields.CheckBoxField(
                    name="new_check", page_number=1, x=100, y=200, required=True
                )
            )
            .create_field(
                Fields.RadioGroup(
                    name="new_radio_group",
                    page_number=1,
                    x=[300, 350, 400],
                    y=[100, 150, 200],
                    required=True,
                )
            )
            .create_field(
                Fields.DropdownField(
                    name="new_dropdown",
                    page_number=1,
                    x=400,
                    y=400,
                    required=True,
                    options=["apple", "banana", "cherry"],
                )
            )
            .create_field(
                Fields.ImageField(
                    name="new_image",
                    page_number=1,
                    x=300,
                    y=600,
                    required=True,
                )
            )
            .create_field(
                Fields.SignatureField(
                    name="new_signature", page_number=1, x=100, y=600, required=True
                )
            )
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_not_required_fields(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_not_required_fields.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(
                Fields.TextField(
                    name="new_text", page_number=1, x=100, y=100, required=False
                )
            )
            .create_field(
                Fields.CheckBoxField(
                    name="new_check", page_number=1, x=100, y=200, required=False
                )
            )
            .create_field(
                Fields.RadioGroup(
                    name="new_radio_group",
                    page_number=1,
                    x=[300, 350, 400],
                    y=[100, 150, 200],
                    required=False,
                )
            )
            .create_field(
                Fields.DropdownField(
                    name="new_dropdown",
                    page_number=1,
                    x=400,
                    y=400,
                    required=False,
                    options=["apple", "banana", "cherry"],
                )
            )
            .create_field(
                Fields.ImageField(
                    name="new_image",
                    page_number=1,
                    x=300,
                    y=600,
                    required=False,
                )
            )
            .create_field(
                Fields.SignatureField(
                    name="new_signature", page_number=1, x=100, y=600, required=False
                )
            )
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_create_fields_with_tooltips(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_fields_with_tooltips.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(
                Fields.TextField(
                    name="new_text", page_number=1, x=100, y=100, tooltip="new_text"
                )
            )
            .create_field(
                Fields.CheckBoxField(
                    name="new_check",
                    page_number=1,
                    x=100,
                    y=200,
                    tooltip="new_checkbox",
                )
            )
            .create_field(
                Fields.RadioGroup(
                    name="new_radio_group",
                    page_number=1,
                    x=[300, 350, 400],
                    y=[100, 150, 200],
                    tooltip="new_radio_group",
                )
            )
            .create_field(
                Fields.DropdownField(
                    name="new_dropdown",
                    page_number=1,
                    x=400,
                    y=400,
                    options=["apple", "banana", "cherry"],
                    tooltip="new_dropdown",
                )
            )
            .create_field(
                Fields.ImageField(
                    name="new_image",
                    page_number=1,
                    x=300,
                    y=600,
                    tooltip="new_image",
                )
            )
            .create_field(
                Fields.SignatureField(
                    name="new_signature",
                    page_number=1,
                    x=100,
                    y=600,
                    tooltip="new_signature",
                )
            )
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
