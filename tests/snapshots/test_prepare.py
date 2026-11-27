# -*- coding: utf-8 -*-

import os

from PyPDFForm import Fields, PdfWrapper


def test_create_checkbox_complex_fill(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_complex_fill.pdf"
    )
    obj = PdfWrapper(template_stream).bulk_create_fields(
        [
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
        ]
    )
    obj.fill(obj.sample_data)

    expect_pdf(obj.read(), expected_path)


def test_create_checkbox_check_fill(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_check_fill.pdf"
    )
    obj = PdfWrapper(template_stream).bulk_create_fields(
        [
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                button_style="check",
            )
        ]
    )
    obj.fill(obj.sample_data)

    expect_pdf(obj.read(), expected_path)


def test_create_checkbox_circle_fill(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_circle_fill.pdf"
    )
    obj = PdfWrapper(template_stream).bulk_create_fields(
        [
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                button_style="circle",
            )
        ]
    )
    obj.fill(obj.sample_data)

    expect_pdf(obj.read(), expected_path)


def test_create_checkbox_cross_fill(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_cross_fill.pdf"
    )
    obj = PdfWrapper(template_stream).bulk_create_fields(
        [
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                button_style="cross",
            )
        ]
    )
    obj.fill(obj.sample_data)

    expect_pdf(obj.read(), expected_path)


def test_create_text_alpha_bg_color(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_alpha_bg_color.pdf"
    )
    obj = PdfWrapper(template_stream).bulk_create_fields(
        [
            Fields.TextField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                bg_color=(0, 0, 1, 0),
            )
        ]
    )

    expect_pdf(obj.read(), expected_path)


def test_create_text_align_center(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_align_center.pdf"
    )
    obj = PdfWrapper(template_stream).bulk_create_fields(
        [
            Fields.TextField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                alignment=1,
            )
        ]
    )

    expect_pdf(obj.read(), expected_path)


def test_create_text_multiline(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_align_multiline.pdf"
    )
    obj = PdfWrapper(template_stream).bulk_create_fields(
        [
            Fields.TextField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
                multiline=True,
            )
        ]
    )

    expect_pdf(obj.read(), expected_path)


def test_create_text_complex_filled(
    template_stream, pdf_samples, sample_font_stream, expect_pdf
):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_text_complex_filled.pdf"
    )
    obj = (
        PdfWrapper(template_stream)
        .register_font("new_font", sample_font_stream)
        .bulk_create_fields(
            [
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
            ]
        )
    )
    obj.fill(obj.sample_data)

    expect_pdf(obj.read(), expected_path)


def test_create_text_comb(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_text_comb.pdf")
    obj = PdfWrapper(template_stream).bulk_create_fields(
        [
            Fields.TextField(
                "foo",
                page_number=1,
                x=100,
                y=100,
                max_length=3,
                comb=True,
            )
        ]
    )

    expect_pdf(obj.read(), expected_path)


def test_create_checkbox_persist_old_widgets_fill(
    template_stream, pdf_samples, expect_pdf
):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_persist_old_widgets_fill.pdf"
    )
    obj = PdfWrapper(template_stream)
    obj.widgets["test"].font_size = 30
    obj.widgets["test"].font_color = (0, 1, 0)
    obj.bulk_create_fields(
        [
            Fields.CheckBoxField(
                name="foo",
                page_number=1,
                x=100,
                y=100,
            )
        ]
    ).fill(obj.sample_data)

    expect_pdf(obj.read(), expected_path)


def test_create_widget_sejda_fill_readonly_before(
    sejda_template, pdf_samples, expect_pdf
):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_widget_sejda_fill_readonly_before.pdf"
    )
    obj = PdfWrapper(sejda_template)
    obj.fill(obj.sample_data, readonly=True).bulk_create_fields(
        [
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
        ]
    ).fill(obj.sample_data)

    expect_pdf(obj.read(), expected_path)


def test_create_widget_sejda_fill_readonly_after(
    sejda_template, pdf_samples, expect_pdf
):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_widget_sejda_fill_readonly_after.pdf"
    )
    obj = PdfWrapper(sejda_template)
    obj.fill(obj.sample_data).bulk_create_fields(
        [
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
        ]
    ).fill(obj.sample_data, readonly=True)

    expect_pdf(obj.read(), expected_path)


def test_fill_cmyk_color(pdf_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "widget", "test_fill_cmyk_color.pdf")
    obj = PdfWrapper(
        os.path.join(pdf_samples, "widget", "sample_template_with_cmyk_color.pdf")
    ).fill({"foo": "foo"})

    expect_pdf(obj.read(), expected_path)


def test_create_radio_complex(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_radio_complex.pdf")
    obj = PdfWrapper(template_stream).bulk_create_fields(
        [
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
        ]
    )

    expect_pdf(obj.read(), expected_path)


def test_create_required_fields(pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_required_fields.pdf"
    )
    obj = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")).bulk_create_fields(
        [
            Fields.TextField(
                name="new_text", page_number=1, x=100, y=100, required=True
            ),
            Fields.CheckBoxField(
                name="new_check", page_number=1, x=100, y=200, required=True
            ),
            Fields.RadioGroup(
                name="new_radio_group",
                page_number=1,
                x=[300, 350, 400],
                y=[100, 150, 200],
                required=True,
            ),
            Fields.DropdownField(
                name="new_dropdown",
                page_number=1,
                x=400,
                y=400,
                required=True,
                options=["apple", "banana", "cherry"],
            ),
            Fields.ImageField(
                name="new_image",
                page_number=1,
                x=300,
                y=600,
                required=True,
            ),
            Fields.SignatureField(
                name="new_signature", page_number=1, x=100, y=600, required=True
            ),
        ]
    )

    expect_pdf(obj.read(), expected_path)


def test_create_not_required_fields(pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_not_required_fields.pdf"
    )
    obj = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")).bulk_create_fields(
        [
            Fields.TextField(
                name="new_text", page_number=1, x=100, y=100, required=False
            ),
            Fields.CheckBoxField(
                name="new_check", page_number=1, x=100, y=200, required=False
            ),
            Fields.RadioGroup(
                name="new_radio_group",
                page_number=1,
                x=[300, 350, 400],
                y=[100, 150, 200],
                required=False,
            ),
            Fields.DropdownField(
                name="new_dropdown",
                page_number=1,
                x=400,
                y=400,
                required=False,
                options=["apple", "banana", "cherry"],
            ),
            Fields.ImageField(
                name="new_image",
                page_number=1,
                x=300,
                y=600,
                required=False,
            ),
            Fields.SignatureField(
                name="new_signature", page_number=1, x=100, y=600, required=False
            ),
        ]
    )

    expect_pdf(obj.read(), expected_path)


def test_create_fields_with_tooltips(pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_fields_with_tooltips.pdf"
    )
    obj = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")).bulk_create_fields(
        [
            Fields.TextField(
                name="new_text", page_number=1, x=100, y=100, tooltip="new_text"
            ),
            Fields.CheckBoxField(
                name="new_check",
                page_number=1,
                x=100,
                y=200,
                tooltip="new_checkbox",
            ),
            Fields.RadioGroup(
                name="new_radio_group",
                page_number=1,
                x=[300, 350, 400],
                y=[100, 150, 200],
                tooltip="new_radio_group",
            ),
            Fields.DropdownField(
                name="new_dropdown",
                page_number=1,
                x=400,
                y=400,
                options=["apple", "banana", "cherry"],
                tooltip="new_dropdown",
            ),
            Fields.ImageField(
                name="new_image",
                page_number=1,
                x=300,
                y=600,
                tooltip="new_image",
            ),
            Fields.SignatureField(
                name="new_signature",
                page_number=1,
                x=100,
                y=600,
                tooltip="new_signature",
            ),
        ]
    )

    expect_pdf(obj.read(), expected_path)


def test_bulk_create_fields_stress_max(pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "bulk_create_fields", "test_bulk_create_fields_stress_max.pdf"
    )

    fields = []
    x = 0
    y = 0
    margin = 25
    while x <= 575:
        while y <= 625:
            fields.append(
                Fields.TextField(f"text_{x}_{y}", 1, x, y, width=margin, height=margin)
            )
            fields.append(Fields.CheckBoxField(f"check_{x}_{y}", 2, x, y, size=margin))
            fields.append(
                Fields.DropdownField(
                    f"dropdown_{x}_{y}",
                    3,
                    x,
                    y,
                    width=margin,
                    height=margin,
                    options=["foo", "bar"],
                )
            )
            fields.append(
                Fields.RadioGroup(
                    f"radio_{x}_{y}", 4, [x, x + 12.5], [y, y + 12.5], size=12.5
                )
            )
            fields.append(
                Fields.ImageField(
                    f"image_{x}_{y}", 5, x, y, width=margin, height=margin
                )
            )
            fields.append(
                Fields.SignatureField(
                    f"signature_{x}_{y}", 6, x, y, width=margin, height=margin
                )
            )
            y += margin
        y = 0
        x += margin

    obj = PdfWrapper()
    for _ in range(6):
        obj += PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
    obj.bulk_create_fields(fields)

    expect_pdf(obj.read(), expected_path)


def test_bulk_create_fields_stress_max_mixed(pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples,
        "bulk_create_fields",
        "test_bulk_create_fields_stress_max_mixed.pdf",
    )

    fields = []
    x = 0
    y = 0
    margin = 25
    while x <= 450:
        while y <= 625:
            fields.append(
                Fields.TextField(f"text_{x}_{y}", 1, x, y, width=margin, height=margin)
            )
            fields.append(
                Fields.CheckBoxField(f"check_{x}_{y}", 1, x + margin, y, size=margin)
            )
            fields.append(
                Fields.DropdownField(
                    f"dropdown_{x}_{y}",
                    1,
                    x,
                    y + margin,
                    width=margin,
                    height=margin,
                    options=["foo", "bar"],
                )
            )
            fields.append(
                Fields.RadioGroup(
                    f"radio_{x}_{y}",
                    1,
                    [x + margin, x + margin + 12.5],
                    [y + margin, y + margin + 12.5],
                    size=12.5,
                )
            )
            fields.append(
                Fields.ImageField(
                    f"image_{x}_{y}",
                    1,
                    x + margin + margin,
                    y,
                    width=margin,
                    height=margin,
                )
            )
            fields.append(
                Fields.SignatureField(
                    f"signature_{x}_{y}",
                    1,
                    x + margin + margin,
                    y + margin,
                    width=margin,
                    height=margin,
                )
            )
            y += 50
        y = 0
        x += 75

    obj = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")).bulk_create_fields(fields)

    expect_pdf(obj.read(), expected_path)
