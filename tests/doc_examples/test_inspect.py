# -*- coding: utf-8 -*-

from PyPDFForm import PdfWrapper


def test_schema(template_stream):
    pdf_form_schema = PdfWrapper(template_stream).schema

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


def test_sample_data(template_stream):
    assert PdfWrapper(template_stream).sample_data == {
        "check": True,
        "check_2": True,
        "check_3": True,
        "test": "test",
        "test_2": "test_2",
        "test_3": "test_3",
    }
