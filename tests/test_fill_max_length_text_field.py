# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_fill_max_length_text_field_all_chars(
    sample_template_with_max_length_text_field,
    max_length_expected_directory,
    expect_pdf,
):
    expected_path = os.path.join(
        max_length_expected_directory, "test_fill_max_length_text_field_all_chars.pdf"
    )
    obj = PdfWrapper(sample_template_with_max_length_text_field).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXXXXXXXXX",
            "Awesomeness": True,
            "Gender": 0,
        }
    )

    expect_pdf(obj.read(), expected_path)


def test_fill_comb_text_field_all_chars(
    sample_template_with_comb_text_field, max_length_expected_directory, expect_pdf
):
    expected_path = os.path.join(
        max_length_expected_directory, "test_fill_comb_text_field_all_chars.pdf"
    )
    obj = PdfWrapper(sample_template_with_comb_text_field).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXXXXXXXXX",
            "Awesomeness": True,
            "Gender": 0,
        }
    )

    expect_pdf(obj.read(), expected_path)


def test_fill_comb_text_field_all_chars_readonly(
    sample_template_with_comb_text_field, max_length_expected_directory, expect_pdf
):
    expected_path = os.path.join(
        max_length_expected_directory,
        "test_fill_comb_text_field_all_chars_readonly.pdf",
    )
    obj = PdfWrapper(sample_template_with_comb_text_field).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXXXXXXXXX",
            "Awesomeness": True,
            "Gender": 0,
        },
        readonly=True,
    )

    expect_pdf(obj.read(), expected_path)


def test_fill_comb_text_field_void(
    sample_template_with_comb_text_field, max_length_expected_directory, expect_pdf
):
    expected_path = os.path.join(
        max_length_expected_directory, "test_fill_comb_text_field_void.pdf"
    )
    obj = PdfWrapper(sample_template_with_comb_text_field).fill({})

    expect_pdf(obj.read(), expected_path)


def test_fill_comb_text_field_even_chars_right_aligned(
    sample_template_with_comb_text_field_right_aligned,
    max_length_expected_directory,
    expect_pdf,
):
    expected_path = os.path.join(
        max_length_expected_directory,
        "test_fill_comb_text_field_even_chars_right_aligned.pdf",
    )
    obj = PdfWrapper(sample_template_with_comb_text_field_right_aligned).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXXXXX",
            "Awesomeness": True,
            "Gender": 0,
        }
    )

    expect_pdf(obj.read(), expected_path)
