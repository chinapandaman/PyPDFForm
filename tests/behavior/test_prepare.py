# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from pypdf import PdfReader

from PyPDFForm import BlankPage, Fields, PdfWrapper
from PyPDFForm.lib.constants import Annots, Subtype, Widget


def test_create_checkbox_complex_fill(template_stream):
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

    assert obj.schema["properties"]["foo"]["type"] == "boolean"


def test_create_text_alpha_bg_color(template_stream):
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
    assert obj.schema["properties"]["foo"]["type"] == "string"


def test_create_text_align_center(template_stream):
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
    assert obj.schema["properties"]["foo"]["type"] == "string"


def test_create_text_multiline(template_stream):
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
    assert obj.schema["properties"]["foo"]["type"] == "string"


def test_create_checkbox_persist_old_widgets_fill(template_stream):
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
    assert obj.schema["properties"]["foo"]["type"] == "boolean"


def test_create_widget_sejda_fill_readonly_before(sejda_template):
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
    assert obj.schema["properties"]["new_text_field_widget"]["type"] == "string"


def test_create_widget_sejda_fill_readonly_after(sejda_template):
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
    assert obj.schema["properties"]["new_text_field_widget"]["type"] == "string"


def test_create_widget_sejda_schema(sejda_template):
    obj = PdfWrapper(sejda_template)
    old_schema = obj.schema
    schema = (
        PdfWrapper(sejda_template)
        .bulk_create_fields(
            [
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
            ]
        )
        .schema
    )

    assert schema["properties"]["new_text_field_widget"]
    assert len(schema["properties"]) == len(old_schema["properties"]) + 1


def test_create_radio_complex(template_stream):
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
    assert obj.schema["properties"]["radio"]["type"] == "integer"


@pytest.mark.slow
def test_bulk_create_fields_stress_max(pdf_samples):
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

    prefix_to_page = {
        "text_": 1,
        "check_": 2,
        "dropdown_": 3,
        "radio_": 4,
        "image_": 5,
        "signature_": 6,
    }

    for k, v in obj.widgets.items():
        for each, page in prefix_to_page.items():
            if k.startswith(each):
                assert v.page_number == page
                break


def test_bulk_create_fields_does_not_duplicate_widgets():
    wrapper = PdfWrapper(BlankPage() * 2)

    fields = []
    y = 760.0
    for i in range(35):
        fields.append(
            Fields.TextField(
                f"p1_field_{i}",
                1,
                50.0,
                y,
                width=220.0,
                height=16.0,
                font_size=9.0,
            )
        )
        y -= 20.0

    y = 760.0
    for i in range(4):
        fields.append(
            Fields.TextField(
                f"p2_field_{i}",
                2,
                50.0,
                y,
                width=220.0,
                height=16.0,
                font_size=9.0,
            )
        )
        y -= 24.0

    output = wrapper.bulk_create_fields(fields).read()
    reader = PdfReader(BytesIO(output))

    widget_count = 0
    for page in reader.pages:
        annots = page.get(Annots) or []
        for annot_ref in annots:
            annot = annot_ref.get_object()
            if str(annot.get(Subtype)) == Widget:
                widget_count += 1

    assert widget_count == len(fields)


def test_bulk_create_fields_failure_creates_nothing(
    template_stream, assert_widgets_match_output
):
    obj = PdfWrapper(template_stream)
    obj.widgets["test"].x = 200
    original = obj.read()
    widgets = dict(obj.widgets)

    # the image field is created before the text field fails
    with pytest.raises(TypeError):
        obj.bulk_create_fields(
            [
                Fields.ImageField("new_image", 1, 100, 100),
                Fields.TextField("new_text", 1, "100", 100),
            ]
        )

    assert obj.widgets == widgets
    assert obj.read() == original
    assert_widgets_match_output(obj)
