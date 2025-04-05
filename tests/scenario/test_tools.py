# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_filling_pdf_escape_pdf_form(tool_pdf_directory, request):
    expected_path = os.path.join(tool_pdf_directory, "pdf_escape_expected.pdf")
    with open(expected_path, "rb+") as f:
        expected = f.read()
        result = PdfWrapper(os.path.join(tool_pdf_directory, "pdf_escape.pdf")).fill(
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

        if os.name != "nt":
            assert len(result.read()) == len(expected)
            assert result.read() == expected


def test_filling_docfly_pdf_form(tool_pdf_directory, request):
    expected_path = os.path.join(tool_pdf_directory, "docfly_expected.pdf")
    with open(expected_path, "rb+") as f:
        expected = f.read()
        result = PdfWrapper(os.path.join(tool_pdf_directory, "docfly.pdf")).fill(
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

        if os.name != "nt":
            assert len(result.read()) == len(expected)
            assert result.read() == expected


def test_filling_sejda_dropdown_pdf_form(tool_pdf_directory, request):
    expected_path = os.path.join(tool_pdf_directory, "sejda_dropdown_expected.pdf")
    with open(expected_path, "rb+") as f:
        expected = f.read()
        result = PdfWrapper(
            os.path.join(tool_pdf_directory, "sejda_dropdown.pdf")
        ).fill({"dropdown_1": 2})
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = result.read()
        assert len(result.read()) == len(expected)
        assert result.read() == expected


def test_filling_soda_pdf_form(tool_pdf_directory, request):
    expected_path = os.path.join(tool_pdf_directory, "soda_expected.pdf")
    with open(expected_path, "rb+") as f:
        expected = f.read()
        result = PdfWrapper(os.path.join(tool_pdf_directory, "soda.pdf")).fill(
            {
                "Text1": "Helvetica 8",
                "Text2": "Helvetica 12",
                "Text3": "Helvetica 24",
                "Text4": "Helvetica 8",
                "Text5": "Helvetica 12",
                "Text6": "Helvetica 24",
                "Text7": "Helvetica 8",
                "Text8": "Helvetica 12",
                "Text9": "Helvetica 24",
            }
        )
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = result.read()

        if os.name != "nt":
            assert len(result.read()) == len(expected)
            assert result.read() == expected


def test_filling_pdfgear_sig(tool_pdf_directory, image_samples, request):
    expected_path = os.path.join(tool_pdf_directory, "pdfgear_expected.pdf")
    with open(expected_path, "rb+") as f:
        expected = f.read()
        result = PdfWrapper(os.path.join(tool_pdf_directory, "pdfgear.pdf")).fill(
            {"signature": os.path.join(image_samples, "sample_signature.png")}
        )
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = result.read()

        if os.name != "nt":
            assert len(result.read()) == len(expected)
            assert result.read() == expected
