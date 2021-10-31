# -*- coding: utf-8 -*-

import os
from PyPDFForm import PyPDFForm2


def test_pdf_form_with_pages_without_elements(pdf_directory):
    obj = PyPDFForm2(os.path.join(
        pdf_directory, "PPF-246.pdf"
    )).fill(
        {
            'QCredit': '5000.63'
        }
    )

    with open(os.path.join(pdf_directory, "PPF-246-expected.pdf"), "rb+") as f:
        assert obj.read() == f.read()
