# -*- coding: utf-8 -*-

import os

from PyPDFForm import PyPDFForm, PyPDFForm2


def test_pdf_form_with_pages_without_elements(pdf_directory):
    obj = PyPDFForm2(os.path.join(pdf_directory, "PPF-246.pdf")).fill(
        {"QCredit": "5000.63"}
    )

    with open(os.path.join(pdf_directory, "PPF-246-expected.pdf"), "rb+") as f:
        assert obj.read() == f.read()


def test_pdf_form_with_pages_without_elements_v1(pdf_directory):
    obj = PyPDFForm(
        os.path.join(pdf_directory, "PPF-246.pdf"), simple_mode=False, sejda=True
    ).fill({"QCredit": "5000.63"})

    with open(os.path.join(pdf_directory, "PPF-246-expected-v1.pdf"), "rb+") as f:
        assert obj.read() == f.read()
