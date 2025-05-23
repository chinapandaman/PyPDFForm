# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_fill_max_length_text_field_all_chars(
    sample_template_with_max_length_text_field, max_length_expected_directory, request
):
    expected_path = os.path.join(
        max_length_expected_directory, "test_fill_max_length_text_field_all_chars.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXXXXXXXX",
                "Awesomeness": True,
                "Gender": 0,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_max_length_text_field_all_chars_flatten(
    sample_template_with_max_length_text_field, max_length_expected_directory, request
):
    expected_path = os.path.join(
        max_length_expected_directory, "test_fill_max_length_text_field_all_chars_flatten.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXXXXXXXX",
                "Awesomeness": True,
                "Gender": 0,
            },
            flatten=True
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_max_length_text_field_odd_chars(
    sample_template_with_max_length_text_field, max_length_expected_directory, request
):
    expected_path = os.path.join(
        max_length_expected_directory, "test_fill_max_length_text_field_odd_chars.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXX",
                "Awesomeness": True,
                "Gender": 0,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_max_length_text_field_odd_chars_flatten(
    sample_template_with_max_length_text_field, max_length_expected_directory, request
):
    expected_path = os.path.join(
        max_length_expected_directory, "test_fill_max_length_text_field_odd_chars_flatten.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXX",
                "Awesomeness": True,
                "Gender": 0,
            },
            flatten=True
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_max_length_text_field_even_chars(
    sample_template_with_max_length_text_field, max_length_expected_directory, request
):
    expected_path = os.path.join(
        max_length_expected_directory, "test_fill_max_length_text_field_even_chars.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXX",
                "Awesomeness": True,
                "Gender": 0,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_max_length_text_field_even_chars_flatten(
    sample_template_with_max_length_text_field, max_length_expected_directory, request
):
    expected_path = os.path.join(
        max_length_expected_directory, "test_fill_max_length_text_field_even_chars_flatten.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXX",
                "Awesomeness": True,
                "Gender": 0,
            },
            flatten=True
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
