# -*- coding: utf-8 -*-

import os

from PyPDFForm import FormWrapper


def test_filling_pdf_escape_pdf_form(tool_pdf_directory, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "scenario", "tools", "pdf_escape_expected.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(os.path.join(tool_pdf_directory, "pdf_escape.pdf")).fill(
            {
                "test_1": "test_1",
                "test_2": "test_2",
                "test_3": "test_3",
                "check_1": True,
                "check_2": True,
                "check_3": True,
                "radio_1": 2,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_filling_docfly_pdf_form(tool_pdf_directory, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "scenario", "tools", "docfly_expected.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(os.path.join(tool_pdf_directory, "docfly.pdf")).fill(
            {
                "test_1": "test_1",
                "test_2": "test_2",
                "test_3": "test_3",
                "check_1": True,
                "check_2": True,
                "check_3": True,
                "radio_1": 1,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected
