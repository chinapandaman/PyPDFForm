# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm.core.constants import Merge as MergeConstants
from PyPDFForm.core.template import Template as TemplateCore
from PyPDFForm.middleware.wrapper import PyPDFForm


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


def test_addition_operator_3_times(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_added_3_copies.pdf"), "rb+") as f:
        result = PyPDFForm()

        for i in range(3):
            result += PyPDFForm(template_stream).fill(data_dict, editable=True)

        page_count = len(TemplateCore().get_elements_by_page(f.read()).keys())
        result_page_count = len(
            TemplateCore().get_elements_by_page(result.stream).keys()
        )
        assert page_count == result_page_count

        for elements in TemplateCore().get_elements_by_page(result.stream).values():
            for element in elements:
                assert (
                    TemplateCore()
                    .get_element_key(element)
                    .split(MergeConstants().separator)[0]
                    in data_dict
                )
