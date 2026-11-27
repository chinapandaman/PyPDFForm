# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper
from tests.support.snapshots import run_sample_template_library_test


def test_need_appearances_fill(template_stream, data_dict, expect_pdf):
    obj = PdfWrapper(template_stream, need_appearances=True).fill(
        data_dict,
    )

    expect_pdf(obj.read())


def test_need_appearances_dropdown_two(sample_template_with_dropdown, expect_pdf):
    obj = PdfWrapper(sample_template_with_dropdown, need_appearances=True).fill(
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

    expect_pdf(obj.read())


def test_need_appearances_fill_sejda_complex(
    sejda_template_complex, sejda_complex_data, expect_pdf
):
    obj = PdfWrapper(sejda_template_complex, need_appearances=True).fill(
        sejda_complex_data,
    )

    expect_pdf(obj.read())


def test_need_appearances_issue_613(pdf_samples, expect_pdf):
    obj = PdfWrapper(
        os.path.join(pdf_samples, "scenario", "issues", "613.pdf"),
        need_appearances=True,
    ).fill(
        {
            "301 Full name": "John Smith",
            "301 Address Street": "1234 road number 6",
        },
    )

    expect_pdf(obj.read())


def test_need_appearances_sample_template_library(
    pdf_samples, image_samples, sample_font_stream, expect_pdf
):
    run_sample_template_library_test(
        pdf_samples,
        image_samples,
        sample_font_stream,
        expect_pdf,
        need_appearances=True,
    )


def test_generate_appearance_streams_fill(template_stream, data_dict, expect_pdf):
    obj = PdfWrapper(template_stream, generate_appearance_streams=True).fill(
        data_dict,
    )

    expect_pdf(obj.read())


def test_generate_appearance_streams_fill_sejda_complex(
    sejda_template_complex, sejda_complex_data, expect_pdf
):
    obj = PdfWrapper(sejda_template_complex, generate_appearance_streams=True).fill(
        sejda_complex_data,
    )

    expect_pdf(obj.read())


def test_generate_appearance_streams_dropdown_two(
    sample_template_with_dropdown, expect_pdf
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

    expect_pdf(obj.read())


def test_generate_appearance_streams_issue_613(pdf_samples, expect_pdf):
    obj = PdfWrapper(
        os.path.join(pdf_samples, "scenario", "issues", "613.pdf"),
        generate_appearance_streams=True,
    ).fill(
        {
            "301 Full name": "John Smith",
            "301 Address Street": "1234 road number 6",
        },
    )

    expect_pdf(obj.read())


def test_generate_appearance_streams_sample_template_library(
    pdf_samples, image_samples, sample_font_stream, expect_pdf
):
    run_sample_template_library_test(
        pdf_samples,
        image_samples,
        sample_font_stream,
        expect_pdf,
        generate_appearance_streams=True,
    )
