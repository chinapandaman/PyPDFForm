# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper
from tests.test_need_appearances import run_sample_template_library_test


def test_fill(
    template_stream, pdf_samples, data_dict, assert_valid_appearances, expect_pdf
):
    expected_path = os.path.join(
        pdf_samples, "generate_appearance_streams", "sample_filled.pdf"
    )
    obj = PdfWrapper(template_stream, generate_appearance_streams=True).fill(
        data_dict,
    )

    expect_pdf(obj.read(), expected_path)
    assert_valid_appearances(obj.read())


def test_fill_sejda_complex(
    sejda_template_complex,
    sejda_complex_data,
    pdf_samples,
    assert_valid_appearances,
    expect_pdf,
):
    expected_path = os.path.join(
        pdf_samples,
        "generate_appearance_streams",
        "paragraph",
        "sample_filled_sejda_complex.pdf",
    )
    obj = PdfWrapper(sejda_template_complex, generate_appearance_streams=True).fill(
        sejda_complex_data,
    )

    expect_pdf(obj.read(), expected_path)
    assert_valid_appearances(obj.read())


def test_dropdown_two(
    sample_template_with_dropdown, pdf_samples, assert_valid_appearances, expect_pdf
):
    expected_path = os.path.join(
        pdf_samples, "generate_appearance_streams", "dropdown", "dropdown_two.pdf"
    )
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

    expect_pdf(obj.read(), expected_path)
    assert_valid_appearances(obj.read())


def test_issue_613(pdf_samples, assert_valid_appearances, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "generate_appearance_streams", "issues", "613_expected.pdf"
    )
    obj = PdfWrapper(
        os.path.join(pdf_samples, "scenario", "issues", "613.pdf"),
        generate_appearance_streams=True,
    ).fill(
        {
            "301 Full name": "John Smith",
            "301 Address Street": "1234 road number 6",
        },
    )

    expect_pdf(obj.read(), expected_path)
    assert_valid_appearances(obj.read())


def test_sample_template_library(
    pdf_samples, image_samples, sample_font_stream, expect_pdf
):
    run_sample_template_library_test(
        pdf_samples,
        image_samples,
        sample_font_stream,
        expect_pdf,
        generate_appearance_streams=True,
    )
