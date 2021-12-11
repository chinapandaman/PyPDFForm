# -*- coding: utf-8 -*-

import os

from PyPDFForm import PyPDFForm2


def test_filling_pdf_escape_pdf_form(tool_pdf_directory):
    with open(os.path.join(tool_pdf_directory, "pdf_escape_expected.pdf"), "rb+") as f:
        expected = f.read()
        result = PyPDFForm2(os.path.join(tool_pdf_directory, "pdf_escape.pdf")).fill(
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
        assert len(result.read()) == len(expected)
        assert (
            result.read()
            == expected
        )
