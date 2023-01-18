# -*- coding: utf-8 -*-

import os

from PyPDFForm import PyPDFForm


def test_fill_max_length_text_field_all_chars(
    sample_template_with_max_length_text_field, max_length_expected_directory
):
    with open(
        os.path.join(max_length_expected_directory, "max_length_text_field_all_chars.pdf"), "rb+"
    ) as f:
        obj = PyPDFForm(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXXXXXXXX",
                "Awesomeness": True,
                "Gender": 0,
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_max_length_text_field_odd_chars(
    sample_template_with_max_length_text_field, max_length_expected_directory
):
    with open(
        os.path.join(max_length_expected_directory, "max_length_text_field_odd_chars.pdf"), "rb+"
    ) as f:
        obj = PyPDFForm(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXX",
                "Awesomeness": True,
                "Gender": 0,
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_max_length_text_field_even_chars(
    sample_template_with_max_length_text_field, max_length_expected_directory
):
    with open(
        os.path.join(max_length_expected_directory, "max_length_text_field_even_chars.pdf"), "rb+"
    ) as f:
        obj = PyPDFForm(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXX",
                "Awesomeness": True,
                "Gender": 0,
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_comb_text_field_all_chars(
    sample_template_with_comb_text_field, max_length_expected_directory
):
    with open(
        os.path.join(max_length_expected_directory, "comb_text_field_all_chars.pdf"), "rb+"
    ) as f:
        obj = PyPDFForm(sample_template_with_comb_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXXXXXXXX",
                "Awesomeness": True,
                "Gender": 0,
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_comb_text_field_odd_chars(
    sample_template_with_comb_text_field, max_length_expected_directory
):
    with open(
        os.path.join(max_length_expected_directory, "comb_text_field_odd_chars.pdf"), "rb+"
    ) as f:
        obj = PyPDFForm(sample_template_with_comb_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXX",
                "Awesomeness": True,
                "Gender": 0,
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_comb_text_field_even_chars(
    sample_template_with_comb_text_field, max_length_expected_directory
):
    with open(
        os.path.join(max_length_expected_directory, "comb_text_field_even_chars.pdf"), "rb+"
    ) as f:
        obj = PyPDFForm(sample_template_with_comb_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXXXX",
                "Awesomeness": True,
                "Gender": 0,
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_comb_text_field_void(
    sample_template_with_comb_text_field, max_length_expected_directory
):
    with open(os.path.join(max_length_expected_directory, "comb_text_field_void.pdf"), "rb+") as f:
        obj = PyPDFForm(sample_template_with_comb_text_field).fill({})

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_comb_text_field_even_chars_right_aligned(
    sample_template_with_comb_text_field_right_aligned, max_length_expected_directory
):
    with open(
        os.path.join(
            max_length_expected_directory, "comb_text_field_even_chars_right_aligned.pdf"
        ),
        "rb+",
    ) as f:
        obj = PyPDFForm(sample_template_with_comb_text_field_right_aligned).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXXXX",
                "Awesomeness": True,
                "Gender": 0,
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected
