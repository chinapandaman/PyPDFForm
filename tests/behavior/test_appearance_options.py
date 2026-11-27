# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_generate_appearance_streams_fill(
    template_stream, data_dict, assert_valid_appearances
):
    obj = PdfWrapper(template_stream, generate_appearance_streams=True).fill(
        data_dict,
    )

    assert_valid_appearances(obj.read())


def test_generate_appearance_streams_fill_sejda_complex(
    sejda_template_complex, sejda_complex_data, assert_valid_appearances
):
    obj = PdfWrapper(sejda_template_complex, generate_appearance_streams=True).fill(
        sejda_complex_data,
    )

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

    assert_valid_appearances(obj.read())
