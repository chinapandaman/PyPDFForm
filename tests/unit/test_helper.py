# -*- coding: utf-8 -*-

import os
import pytest
from copy import deepcopy

from PyPDFForm.middleware.helper import Template, Elements
from PyPDFForm.middleware.constants import Template as TemplateConstants


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


def test_iterate_elements(template_stream, data_dict):
    _data_dict = deepcopy(data_dict)

    for k in _data_dict.keys():
        _data_dict[k] = False

    for each in Template().iterate_elements(template_stream):
        _data_dict[each[TemplateConstants().annotation_field_key][1:-1]] = True

    for k in _data_dict.keys():
        assert _data_dict[k]


def test_build_elements(template_stream, data_dict):
    _data_dict = deepcopy(data_dict)

    for k in _data_dict.keys():
        _data_dict[k] = False

    for k, v in Elements().build_elements(template_stream).items():
        if (
            k in _data_dict
            and k == v.name
        ):
            _data_dict[k] = True

    for k in _data_dict.keys():
        assert _data_dict[k]
