# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import PyPDFForm


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
    sample_template_with_max_length_text_field
):
    assert PyPDFForm(sample_template_with_max_length_text_field).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXXXXXXXXX",
            "Awesomeness": True,
            "Gender": 0
        }
    ).read()

    # Todo: finish test on windows machine


def test_fill_max_length_text_field_odd_chars(
    sample_template_with_max_length_text_field
):
    assert PyPDFForm(sample_template_with_max_length_text_field).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXX",
            "Awesomeness": True,
            "Gender": 0
        }
    ).read()

    # Todo: finish test on windows machine


def test_fill_max_length_text_field_even_chars(
    sample_template_with_max_length_text_field
):
    assert PyPDFForm(sample_template_with_max_length_text_field).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXXX",
            "Awesomeness": True,
            "Gender": 0
        }
    ).read()

    # Todo: finish test on windows machine


def test_fill_comb_text_field_all_chars(
    sample_template_with_comb_text_field
):
    assert PyPDFForm(sample_template_with_comb_text_field).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXXXXXXXXX",
            "Awesomeness": True,
            "Gender": 0
        }
    ).read()

    # Todo: finish test on windows machine


def test_fill_comb_text_field_odd_chars(
    sample_template_with_comb_text_field
):
    assert PyPDFForm(sample_template_with_comb_text_field).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXX",
            "Awesomeness": True,
            "Gender": 0
        }
    ).read()

    # Todo: finish test on windows machine


def test_fill_comb_text_field_even_chars(
    sample_template_with_comb_text_field
):
    assert PyPDFForm(sample_template_with_comb_text_field).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXXX",
            "Awesomeness": True,
            "Gender": 0
        }
    ).read()

    # Todo: finish test on windows machine
