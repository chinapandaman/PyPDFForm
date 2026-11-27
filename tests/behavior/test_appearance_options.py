# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pikepdf
import pytest

from PyPDFForm import Fields, PdfWrapper
from tests.support.builders import save, set_default_appearance, with_parent_cycle
from tests.support.checks import find_widget, get_normal_appearance


@pytest.mark.parametrize(
    ("properties", "value", "generated"),
    [
        ({}, "plain text", True),
        ({}, "café naïve", True),
        ({}, "한국어 테스트", False),
        ({"multiline": True}, "one line", False),
        ({"alignment": 0}, "left", True),
        ({"alignment": 1}, "centered", False),
        ({"alignment": 2}, "right", False),
        ({"comb": True, "max_length": 6}, "ABCDEF", False),
        ({"font": "registered"}, "registered font", True),
        ({"font": "registered"}, "Ωmega", False),
    ],
    ids=[
        "ascii",
        "winansi",
        "korean",
        "multiline",
        "left",
        "center",
        "right",
        "comb",
        "registered-font",
        "outside-font-encoding",
    ],
)
def test_generated_text_appearance_fallback(
    template_stream,
    sample_font_stream,
    properties,
    value,
    generated,
    assert_valid_appearances,
):
    form = PdfWrapper(template_stream, generate_appearance_streams=True)
    form.register_font("registered", sample_font_stream)
    for attribute, setting in properties.items():
        setattr(form.widgets["test"], attribute, setting)

    output = form.fill({"test": value, "test_2": "other"}).read()

    # the generator can't draw it, so PDF viewers draw it from its value
    assert_valid_appearances(output)
    assert ("/AP" in find_widget(output, "test")) is generated
    assert b"(other) Tj" in get_normal_appearance(output, "test_2")


@pytest.mark.parametrize(
    ("options", "generated"),
    [(["apple", "grape"], True), ([("apple", "A"), ("grape", "G")], False)],
    ids=["same-export", "other-export"],
)
def test_generated_dropdown_appearance_fallback(template_stream, options, generated):
    form = PdfWrapper(template_stream, generate_appearance_streams=True)
    form.bulk_create_fields(
        [Fields.DropdownField(name="new", page_number=1, x=100, y=300, options=options)]
    )

    # the generator would draw the export value
    output = form.fill({"new": 1}).read()

    assert ("/AP" in find_widget(output, "new")) is generated


@pytest.mark.parametrize(
    ("default_appearance", "value", "generated"),
    [
        ("/Missing 0 Tf 0 g", "plain text", True),
        ("/Missing 0 Tf 0 g", "café", False),
    ],
    ids=["ascii", "not-ascii"],
)
def test_generated_appearance_fallback_without_font(
    template_stream, default_appearance, value, generated
):
    # a font that isn't in the resources is drawn in ASCII
    template = set_default_appearance(template_stream, "test", default_appearance)

    output = PdfWrapper(template, generate_appearance_streams=True)
    output = output.fill({"test": value}).read()

    assert ("/AP" in find_widget(output, "test")) is generated


def test_generated_appearance_fallback_with_form_alignment(template_stream):
    with pikepdf.Pdf.open(BytesIO(template_stream)) as pdf:
        pdf.Root.AcroForm.Q = 1
        template = save(pdf)

    output = PdfWrapper(template, generate_appearance_streams=True)
    output = output.fill({"test": "centered"}).read()

    # the fields are centered by the form's default
    assert "/AP" not in find_widget(output, "test")


def test_generated_appearance_fallback_with_parent_cycle(
    template_stream, assert_valid_appearances
):
    template = with_parent_cycle(template_stream, "test")

    output = PdfWrapper(template, generate_appearance_streams=True)
    output = output.fill({"test_2": "café"}).read()

    # entries above the field can't be resolved, so it reads as having none
    assert_valid_appearances(output)
    assert "/AP" in find_widget(output, "test")


@pytest.mark.parametrize(
    "path",
    [
        ["test_fill.pdf"],
        ["dropdown", "test_dropdown_one.pdf"],
        ["dropdown", "test_dropdown_two.pdf"],
    ],
)
@pytest.mark.parametrize(
    "options",
    [{}, {"need_appearances": True}],
    ids=["default", "need-appearances"],
)
def test_output_without_invalid_appearances(
    pdf_samples, path, options, assert_valid_appearances
):
    # written by an earlier version, with a value string as /AP
    with open(os.path.join(pdf_samples, *path), "rb") as f:
        template = f.read()
    with pytest.raises(AssertionError):
        assert_valid_appearances(template)

    form = PdfWrapper(template, **options)

    assert_valid_appearances(form.read())
    assert_valid_appearances(form.fill({}).read())


def test_generate_appearance_streams_fill(
    template_stream, data_dict, assert_valid_appearances
):
    obj = PdfWrapper(template_stream, generate_appearance_streams=True).fill(
        data_dict,
    )

    # a second read of the same wrapper also has valid appearances
    obj.read()
    assert_valid_appearances(obj.read())


def test_generate_appearance_streams_fill_sejda_complex(
    sejda_template_complex, sejda_complex_data, assert_valid_appearances
):
    obj = PdfWrapper(sejda_template_complex, generate_appearance_streams=True).fill(
        sejda_complex_data,
    )

    # a second read of the same wrapper also has valid appearances
    obj.read()
    assert_valid_appearances(obj.read())


def test_generate_appearance_streams_dropdown_two(
    sample_template_with_dropdown, assert_valid_appearances
):
    obj = PdfWrapper(
        sample_template_with_dropdown, generate_appearance_streams=True
    ).fill(
        {
            "test_1": "test_1",
            "test_2": "test_2",
            "test_3": "test_3",
            "check_1": True,
            "check_2": True,
            "check_3": True,
            "radio_1": 1,
            "dropdown_1": 1,
        },
    )

    # a second read of the same wrapper also has valid appearances
    obj.read()
    assert_valid_appearances(obj.read())


def test_generate_appearance_streams_issue_613(pdf_samples, assert_valid_appearances):
    obj = PdfWrapper(
        os.path.join(pdf_samples, "scenario", "issues", "613.pdf"),
        generate_appearance_streams=True,
    ).fill(
        {
            "301 Full name": "John Smith",
            "301 Address Street": "1234 road number 6",
        },
    )

    # a second read of the same wrapper also has valid appearances
    obj.read()
    assert_valid_appearances(obj.read())
