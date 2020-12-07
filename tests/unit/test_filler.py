# -*- coding: utf-8 -*-

import os
import pdfrw
import pytest

from PyPDFForm.core.filler import Filler
from PyPDFForm.core.template import Template as TemplateCore
from PyPDFForm.core.utils import Utils
from PyPDFForm.core.constants import Filler as FillerConstants


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples")


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
    result_stream = Filler().simple_fill(template_stream, converted_data)

    for element in TemplateCore().iterate_elements(result_stream):
        key = TemplateCore().get_element_key(element)

        if isinstance(data_dict[key], bool):
            assert element[FillerConstants().checkbox_field_value_key] == (
                pdfrw.PdfName.Yes if data_dict[key] else pdfrw.PdfName.Off
            )
        else:
            assert element[FillerConstants().text_field_value_key][1:-1] == data_dict[key]
