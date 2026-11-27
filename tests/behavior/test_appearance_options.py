# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import PdfWrapper


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
