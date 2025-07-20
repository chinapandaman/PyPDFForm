# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_schema(static_pdfs):
    pdf_form_schema = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf")
    ).schema

    assert pdf_form_schema == {
        "type": "object",
        "properties": {
            "test": {"type": "string"},
            "check": {"type": "boolean"},
            "test_2": {"type": "string"},
            "check_2": {"type": "boolean"},
            "test_3": {"type": "string"},
            "check_3": {"type": "boolean"},
        },
    }


def test_data(static_pdfs):
    assert PdfWrapper(os.path.join(static_pdfs, "sample_template_filled.pdf")).data == {
        "check": True,
        "check_2": True,
        "check_3": True,
        "test": "test",
        "test_2": "test2",
        "test_3": "test3",
    }


def test_sample_data(static_pdfs):
    assert PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).sample_data == {
        "check": True,
        "check_2": True,
        "check_3": True,
        "test": "test",
        "test_2": "test_2",
        "test_3": "test_3",
    }
