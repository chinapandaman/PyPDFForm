# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_fill(static_pdfs, expect_pdf):
    expected_path = os.path.join(static_pdfs, "sample_filled.pdf")

    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf"),
        need_appearances=True,
    ).fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
    )

    expect_pdf(filled.read(), expected_path)
