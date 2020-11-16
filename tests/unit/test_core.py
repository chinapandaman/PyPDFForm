# -*- coding: utf-8 -*-

import os
import uuid
from copy import deepcopy

import pdfrw
import pytest
from PyPDFForm.core import _PyPDFForm


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
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
        elements = result_pdf.pages[i][obj._ANNOT_KEY]
        if elements:
            for element in elements:
                if (
                    element[obj._SUBTYPE_KEY] == obj._WIDGET_SUBTYPE_KEY
                    and element[obj._ANNOT_FIELD_KEY]
                ):
                    key = element[obj._ANNOT_FIELD_KEY][1:-1]

                    expected = obj._data_dict[key]
                    if isinstance(expected, bool):
                        assert element["/AS"] == (
                            pdfrw.PdfName.Yes if expected else pdfrw.PdfName.Off
                        )
                    else:
                        assert element["/V"][1:-1] == expected


def test_assign_uuid(template_stream):
    obj = _PyPDFForm()
    result_pdf = pdfrw.PdfReader(
        fdata=obj._assign_uuid(template_stream, editable=False)
    )

    _uuid = {}

    for i in range(len(result_pdf.pages)):
        elements = result_pdf.pages[i][obj._ANNOT_KEY]
        if elements:
            for element in elements:
                if (
                    element[obj._SUBTYPE_KEY] == obj._WIDGET_SUBTYPE_KEY
                    and element[obj._ANNOT_FIELD_KEY]
                ):
                    assert element["/Ff"] == pdfrw.PdfObject(1)
                    key = element[obj._ANNOT_FIELD_KEY][1:-1]
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

    obj = _PyPDFForm().build_elements(template_stream)
    obj._data_dict = deepcopy(_data)
    obj._bool_to_checkboxes()
    result_pdf = pdfrw.PdfReader(fdata=obj._fill_pdf_canvas(template_stream, 0, 0))

    for i in range(len(result_pdf.pages)):
        elements = result_pdf.pages[i][obj._ANNOT_KEY]
        if elements:
            for element in elements:
                if (
                    element[obj._SUBTYPE_KEY] == obj._WIDGET_SUBTYPE_KEY
                    and element[obj._ANNOT_FIELD_KEY]
                ):
                    key = element[obj._ANNOT_FIELD_KEY][1:-1]
                    expected = _data[key]

                    if not isinstance(expected, bool):
                        assert False

                    assert element["/AS"] == (
                        pdfrw.PdfName.Yes if expected else pdfrw.PdfName.Off
                    )


def test_merging(template_stream):
    obj_one = _PyPDFForm()
    obj_two = _PyPDFForm()

    obj_one.stream = template_stream
    obj_two.stream = template_stream

    result = pdfrw.PdfReader(fdata=(obj_one + obj_two).stream)

    assert len(result.pages) == len(pdfrw.PdfReader(fdata=template_stream).pages) * 2


def test_editable(template_stream):
    obj = _PyPDFForm()
    result_pdf = pdfrw.PdfReader(fdata=obj._assign_uuid(template_stream, editable=True))

    for i in range(len(result_pdf.pages)):
        elements = result_pdf.pages[i][obj._ANNOT_KEY]
        if elements:
            for element in elements:
                if (
                    element[obj._SUBTYPE_KEY] == obj._WIDGET_SUBTYPE_KEY
                    and element[obj._ANNOT_FIELD_KEY]
                ):
                    assert element["/Ff"] is None


def test_build_elements(template_stream):
    _data = {
        "test": False,
        "check": False,
        "test_2": False,
        "check_2": False,
        "test_3": False,
        "check_3": False,
    }

    obj = _PyPDFForm().build_elements(template_stream)

    for each in obj.elements.keys():
        _data[each] = True

    for k in _data.keys():
        assert _data[k]


def test_update_elements(template_stream):
    _data = {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    }

    obj = (
        _PyPDFForm()
        .build_elements(template_stream)
        .fill(
            template_stream,
            _data,
            simple_mode=False,
            font_size=20,
            text_x_offset=0,
            text_y_offset=0,
            text_wrap_length=100,
            editable=False,
        )
    )

    for k, v in obj.elements.items():
        assert _data[k] == v.value

        if v.type == "text":
            assert v.font_size == 20
            assert v.text_x_offset == 0
            assert v.text_y_offset == 0
            assert v.text_wrap_length == 100
