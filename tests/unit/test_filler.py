# -*- coding: utf-8 -*-

import os

import pdfrw
import pytest

from PyPDFForm.core.constants import Template as TemplateConstants
from PyPDFForm.core.filler import Filler
from PyPDFForm.core.template import Template as TemplateCore
from PyPDFForm.core.utils import Utils


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "v2")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def data_dict():
    return {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    }


def test_simple_fill(template_stream, data_dict):
    converted_data = Utils.bool_to_checkboxes(data_dict)
    result_stream = Filler().simple_fill(template_stream, converted_data, False)

    for element in TemplateCore().iterate_elements(result_stream):
        key = TemplateCore().get_element_key(element)

        if isinstance(data_dict[key], bool):
            assert element[TemplateConstants().checkbox_field_value_key] == (
                pdfrw.PdfName.Yes if data_dict[key] else pdfrw.PdfName.Off
            )
        else:
            assert (
                element[TemplateConstants().text_field_value_key][1:-1]
                == data_dict[key]
            )
        assert element[TemplateConstants().field_editable_key] == pdfrw.PdfObject(1)
