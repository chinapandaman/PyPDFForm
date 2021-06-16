# -*- coding: utf-8 -*-

import os
from copy import deepcopy

import pdfrw
import pytest

from PyPDFForm.core.template import Template as TemplateCore
from PyPDFForm.core.utils import Utils
from PyPDFForm.middleware.constants import Text as TextConstants
from PyPDFForm.middleware.element import Element, ElementType


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


def test_generate_stream(template_stream, data_dict):
    template = TemplateCore().get_elements_by_page(template_stream)
    result = TemplateCore().get_elements_by_page(
        Utils.generate_stream(pdfrw.PdfReader(fdata=template_stream))
    )

    page_count = len(template.keys())
    result_page_count = len(result.keys())
    for elements in result.values():
        for element in elements:
            assert TemplateCore().get_element_key(element) in data_dict

    assert page_count == result_page_count


def test_bool_to_checkboxes(data_dict):
    result = deepcopy(data_dict)

    for k, v in Utils().bool_to_checkboxes(result).items():
        if isinstance(data_dict[k], bool):
            assert v == (pdfrw.PdfName.Yes if data_dict[k] else pdfrw.PdfName.Off)


def test_bool_to_checkbox():
    assert Utils().bool_to_checkbox(True) == pdfrw.PdfName.Yes
    assert Utils().bool_to_checkbox(False) == pdfrw.PdfName.Off


def checkbox_radio_to_draw():
    new_checkbox_element = Element("foo", ElementType.checkbox, True)
    new_radio_element = Element("bar", ElementType.radio, 0)

    new_checkbox_to_draw = Utils().checkbox_radio_to_draw(new_checkbox_element)
    new_radio_to_draw = Utils().checkbox_radio_to_draw(new_radio_element)

    assert new_checkbox_to_draw.value == u"\u2713"
    assert new_checkbox_to_draw.type == ElementType.text
    assert new_checkbox_to_draw.name == "foo"
    assert new_checkbox_to_draw.font == TextConstants().global_font
    assert new_checkbox_to_draw.font_size == TextConstants().global_font_size
    assert new_checkbox_to_draw.font_color == TextConstants().global_font_color
    assert new_checkbox_to_draw.text_x_offset == TextConstants().global_text_x_offset
    assert new_checkbox_to_draw.text_y_offset == TextConstants().global_text_y_offset
    assert (
        new_checkbox_to_draw.text_wrap_length == TextConstants().global_text_wrap_length
    )

    assert new_radio_to_draw.value == u"\u25CF"
    assert new_radio_to_draw.type == ElementType.text
    assert new_radio_to_draw.name == "bar"
    assert new_radio_to_draw.font == TextConstants().global_font
    assert new_radio_to_draw.font_size == TextConstants().global_font_size
    assert new_radio_to_draw.font_color == TextConstants().global_font_color
    assert new_radio_to_draw.text_x_offset == TextConstants().global_text_x_offset
    assert new_radio_to_draw.text_y_offset == TextConstants().global_text_y_offset
    assert new_radio_to_draw.text_wrap_length == TextConstants().global_text_wrap_length


def test_merge_two_pdfs(template_stream, data_dict):
    template = TemplateCore().get_elements_by_page(template_stream)
    result = TemplateCore().get_elements_by_page(
        Utils().merge_two_pdfs(template_stream, template_stream)
    )

    page_count = len(template.keys())
    merged_page_count = len(result.keys())
    for elements in result.values():
        for element in elements:
            assert TemplateCore().get_element_key(element) in data_dict

    assert page_count * 2 == merged_page_count
