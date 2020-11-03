# -*- coding: utf-8 -*-

import os
import uuid
from copy import deepcopy

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


def test_bool_to_checkboxes():
    _data = {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    }

    obj = _PyPDFForm()
    obj._data_dict = deepcopy(_data)
    obj._bool_to_checkboxes()

    for k, v in obj._data_dict.items():
        if isinstance(_data[k], bool):
            assert v == (pdfrw.PdfName.Yes if _data[k] else pdfrw.PdfName.Off)


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
    obj._bool_to_checkboxes()
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
                        assert annotation["/AS"] == (
                            pdfrw.PdfName.Yes if expected else pdfrw.PdfName.Off
                        )
                    else:
                        assert annotation["/V"][1:-1] == expected


def test_assign_uuid(template_stream):
    obj = _PyPDFForm()
    result_pdf = pdfrw.PdfReader(fdata=obj._assign_uuid(template_stream))

    _uuid = {}

    for i in range(len(result_pdf.pages)):
        annotations = result_pdf.pages[i][obj._ANNOT_KEY]
        if annotations:
            for annotation in annotations:
                if (
                    annotation[obj._SUBTYPE_KEY] == obj._WIDGET_SUBTYPE_KEY
                    and annotation[obj._ANNOT_FIELD_KEY]
                ):
                    key = annotation[obj._ANNOT_FIELD_KEY][1:-1]
                    _uuid[key.split("_")[-1]] = True

    for each in _uuid.keys():
        assert len(each) == len(uuid.uuid4().hex)

    assert len(_uuid.keys()) == 1


def test_fill_pdf_canvas(template_stream):
    _data = {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    }

    obj = _PyPDFForm()
    obj._data_dict = deepcopy(_data)
    obj._bool_to_checkboxes()
    result_pdf = pdfrw.PdfReader(fdata=obj._fill_pdf_canvas(template_stream))

    for i in range(len(result_pdf.pages)):
        annotations = result_pdf.pages[i][obj._ANNOT_KEY]
        if annotations:
            for annotation in annotations:
                if (
                    annotation[obj._SUBTYPE_KEY] == obj._WIDGET_SUBTYPE_KEY
                    and annotation[obj._ANNOT_FIELD_KEY]
                ):
                    key = annotation[obj._ANNOT_FIELD_KEY][1:-1]
                    expected = _data[key]

                    if not isinstance(expected, bool):
                        assert False

                    assert annotation["/AS"] == (
                        pdfrw.PdfName.Yes if expected else pdfrw.PdfName.Off
                    )
