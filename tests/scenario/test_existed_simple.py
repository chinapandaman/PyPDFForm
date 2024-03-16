# -*- coding: utf-8 -*-

import os

from PyPDFForm import FormWrapper


def test_ds82(existed_pdf_directory, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "scenario", "existed", "DS82_expected.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(os.path.join(existed_pdf_directory, "DS82.pdf")).fill(
            {
                "LastName": "Smith",
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_ds82_all_chars_lowercase(existed_pdf_directory, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "scenario", "existed", "DS82_expected_all_chars_lowercase.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(os.path.join(existed_pdf_directory, "DS82.pdf")).fill(
            {
                "LastName": "x" * 30,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_ds82_all_chars_uppercase(existed_pdf_directory, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "scenario", "existed", "DS82_expected_all_chars_uppercase.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(os.path.join(existed_pdf_directory, "DS82.pdf")).fill(
            {
                "LastName": "X" * 30,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_ds82_mixed_case(existed_pdf_directory, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "scenario", "existed", "DS82_expected_mixed_case.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(os.path.join(existed_pdf_directory, "DS82.pdf")).fill(
            {
                "LastName": "xX" * 10,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_illinois_real_estate_power_of_attorney_form(existed_pdf_directory, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "scenario", "existed",
                                 "illinois-real-estate-power-of-attorney-form_expected.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(os.path.join(existed_pdf_directory, "illinois-real-estate-power-of-attorney-form.pdf")).fill(
            {
                "undefined": "John Doe",
                "State of": "Chicago",
                "undefined_2": "Illinois",
                "of": "Michael Smith",
                "Illinois as my Attorneyin": "Chicago",
                "with full power and": "Random",
                "is as": "Not Random",
                "Address of Principal": "1 N Central, Chicago, IL 60000",
                "Phone number where Principal can be contacted": "(000)000-0000",
                "Email address of Principal": "msmith@example.com",
                "Text3": "Someone",
                "Dated": "2018-01-01",
                "Text4": "Sometwo",
                "Text5": "Somethree",
                "Text6": "Somefour",
                "Dated 1": "2019-01-01",
                "My commission expires": "NOW",
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected
