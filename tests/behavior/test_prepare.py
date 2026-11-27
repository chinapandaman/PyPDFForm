# -*- coding: utf-8 -*-

from io import BytesIO

import pytest
from pypdf import PdfReader

from PyPDFForm import BlankPage, Fields, PdfWrapper
from PyPDFForm.lib.constants import Annots, Subtype, Widget


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
