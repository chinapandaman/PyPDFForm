# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import PyPDFForm2


@pytest.fixture
def expected_directory():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "max_length_text_field_related")


@pytest.fixture
def sample_template_with_max_length_text_field(pdf_samples):
    with open(
            os.path.join(pdf_samples, "sample_template_with_max_length_text_field.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_comb_text_field(pdf_samples):
    with open(
            os.path.join(pdf_samples, "sample_template_with_comb_text_field.pdf"), "rb+"
    ) as f:
        return f.read()


def test_fill_max_length_text_field_all_chars(
    sample_template_with_max_length_text_field, expected_directory
):
    with open(os.path.join(expected_directory, "max_length_text_field_all_chars.pdf"), "rb+") as f:
        obj = PyPDFForm2(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXXXXXXXX",
                "Awesomeness": True,
                "Gender": 0
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_max_length_text_field_odd_chars(
    sample_template_with_max_length_text_field, expected_directory
):
    with open(os.path.join(expected_directory, "max_length_text_field_odd_chars.pdf"), "rb+") as f:
        obj = PyPDFForm2(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXX",
                "Awesomeness": True,
                "Gender": 0
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_max_length_text_field_even_chars(
    sample_template_with_max_length_text_field, expected_directory
):
    with open(os.path.join(expected_directory, "max_length_text_field_even_chars.pdf"), "rb+") as f:
        obj = PyPDFForm2(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXX",
                "Awesomeness": True,
                "Gender": 0
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_comb_text_field_all_chars(
    sample_template_with_comb_text_field, expected_directory
):
    with open(os.path.join(expected_directory, "comb_text_field_all_chars.pdf"), "rb+") as f:
        obj = PyPDFForm2(sample_template_with_comb_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXXXXXXXX",
                "Awesomeness": True,
                "Gender": 0
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_comb_text_field_odd_chars(
    sample_template_with_comb_text_field, expected_directory
):
    with open(os.path.join(expected_directory, "comb_text_field_odd_chars.pdf"), "rb+") as f:
        obj = PyPDFForm2(sample_template_with_comb_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXX",
                "Awesomeness": True,
                "Gender": 0
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_comb_text_field_even_chars(
    sample_template_with_comb_text_field, expected_directory
):
    with open(os.path.join(expected_directory, "comb_text_field_even_chars.pdf"), "rb+") as f:
        obj = PyPDFForm2(sample_template_with_comb_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXXXX",
                "Awesomeness": True,
                "Gender": 0
            }
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected
