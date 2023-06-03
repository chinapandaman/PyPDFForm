# -*- coding: utf-8 -*-

import os

from PyPDFForm import PyPDFForm


def test_pdf_form_with_pages_without_elements(issue_pdf_directory, request):
    obj = PyPDFForm(os.path.join(issue_pdf_directory, "PPF-246.pdf")).fill(
        {"QCredit": "5000.63"}
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-246-expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_pdf_form_with_central_aligned_text_fields(issue_pdf_directory, request):
    obj = PyPDFForm(os.path.join(issue_pdf_directory, "PPF-285.pdf")).fill(
        {
            "name": "Hans Mustermann",
            "fulladdress": "Musterstr. 12, 82903 Musterdorf, Musterland",
            "advisorname": "Karl Test",
        }
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-285-expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_pdf_form_with_central_aligned_text_fields_void(issue_pdf_directory):
    assert PyPDFForm(os.path.join(issue_pdf_directory, "PPF-285.pdf")).fill({}).read()
