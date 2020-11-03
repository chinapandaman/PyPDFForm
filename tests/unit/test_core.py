# -*- coding: utf-8 -*-

import os

import pdfrw
import pytest
from PyPDFForm.pdf import _PyPDFForm


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def image_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_image.jpg"), "rb+") as f:
        return f.read()


def test_simple_mode_fill_pdf_method(template_stream):
    obj = _PyPDFForm()
    obj._data_dict = {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    }
    result_pdf = pdfrw.PdfReader(fdata=obj._fill_pdf(template_stream))

    for i in range(len(result_pdf.pages)):
        annotations = result_pdf.pages[i][obj._ANNOT_KEY]
        if annotations:
            for annotation in annotations:
                if (
                    annotation[obj._SUBTYPE_KEY] == obj._WIDGET_SUBTYPE_KEY
                    and annotation[obj._ANNOT_FIELD_KEY]
                ):
                    key = annotation[obj._ANNOT_FIELD_KEY][1:-1]

                    expected = obj._data_dict[key]
                    if isinstance(expected, bool):
                        assert annotation["/AS"] == pdfrw.PdfObject(expected)
                    else:
                        assert annotation["/V"][1:-1] == expected
