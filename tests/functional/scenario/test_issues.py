# -*- coding: utf-8 -*-

import os

from PyPDFForm import PyPDFForm, PyPDFForm2


def test_pdf_form_with_pages_without_elements(issue_pdf_directory):
    obj = PyPDFForm2(os.path.join(issue_pdf_directory, "PPF-246.pdf")).fill(
        {"QCredit": "5000.63"}
    )

    with open(os.path.join(issue_pdf_directory, "PPF-246-expected.pdf"), "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_pdf_form_with_pages_without_elements_v1(issue_pdf_directory):
    obj = PyPDFForm(
        os.path.join(issue_pdf_directory, "PPF-246.pdf"), simple_mode=False, sejda=True
    ).fill({"QCredit": "5000.63"})

    with open(os.path.join(issue_pdf_directory, "PPF-246-expected-v1.pdf"), "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_pdf_form_with_central_aligned_text_fields(issue_pdf_directory):
    obj = PyPDFForm2(
        os.path.join(issue_pdf_directory, "PPF-285.pdf")
    ).fill({
        "name": "Hans Mustermann",
        "fulladdress": "Musterstr. 12, 82903 Musterdorf, Musterland",
        "advisorname": "Karl Test"
    })

    with open(os.path.join(issue_pdf_directory, "PPF-285-expected.pdf"), "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
