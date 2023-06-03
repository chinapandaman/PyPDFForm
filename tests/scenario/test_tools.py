# -*- coding: utf-8 -*-

import os

from PyPDFForm import PyPDFForm


def test_filling_pdf_escape_pdf_form(tool_pdf_directory, request):
    expected_path = os.path.join(tool_pdf_directory, "pdf_escape_expected.pdf")
    with open(expected_path, "rb+") as f:
        expected = f.read()
        result = PyPDFForm(os.path.join(tool_pdf_directory, "pdf_escape.pdf")).fill(
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
        request.config.results["stream"] = result.read()
        assert len(result.read()) == len(expected)
        assert result.read() == expected


def test_filling_docfly_pdf_form(tool_pdf_directory, request):
    expected_path = os.path.join(tool_pdf_directory, "docfly_expected.pdf")
    with open(expected_path, "rb+") as f:
        expected = f.read()
        result = PyPDFForm(os.path.join(tool_pdf_directory, "docfly.pdf")).fill(
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
        request.config.results["stream"] = result.read()
        assert len(result.read()) == len(expected)
        assert result.read() == expected


def test_filling_sejda_dropdown_pdf_form(tool_pdf_directory, request):
    expected_path = os.path.join(tool_pdf_directory, "sejda_dropdown_expected.pdf")
    with open(expected_path, "rb+") as f:
        expected = f.read()
        result = PyPDFForm(os.path.join(tool_pdf_directory, "sejda_dropdown.pdf")).fill(
            {"dropdown_1": 2}
        )
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = result.read()
        assert len(result.read()) == len(expected)
        assert result.read() == expected
