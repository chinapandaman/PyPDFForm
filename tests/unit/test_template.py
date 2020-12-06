# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm.middleware.template import Template


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
        "test": False,
        "check": False,
        "test_2": False,
        "check_2": False,
        "test_3": False,
        "check_3": False,
    }


def test_iterate_elements_and_get_element_key(template_stream, data_dict):
    for each in Template().iterate_elements(template_stream):
        data_dict[Template().get_element_key(each)] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_build_elements(template_stream, data_dict):
    for k, v in Template().build_elements(template_stream).items():
        if k in data_dict and k == v.name:
            data_dict[k] = True

    for k in data_dict.keys():
        assert data_dict[k]
