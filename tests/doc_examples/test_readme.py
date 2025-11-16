# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_fill(static_pdfs, request):
    expected_path = os.path.join(static_pdfs, "sample_filled.pdf")

    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf"),
        generate_appearance_streams=True,
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

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = filled.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(filled.read()) == len(expected)
        request.config.results["skip_regenerate"] = len(filled.read()) == len(expected)
