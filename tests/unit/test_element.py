# -*- coding: utf-8 -*-

import pytest
from PyPDFForm.middleware.element import Element


@pytest.fixture
def text_element_attributes():
    return [
        "font_size",
        "font_color",
        "text_x_offset",
        "text_y_offset",
        "text_wrap_length",
    ]


def test_constructing_text_element(text_element_attributes):
    obj = Element("foo", "text")

    assert obj.name == "foo"
    assert obj.type == "text"

    assert not obj.value

    for each in text_element_attributes:
        assert hasattr(obj, each)


def test_constructing_checkboxes_element(text_element_attributes):
    obj = Element("foo", "checkbox")

    assert obj.name == "foo"
    assert obj.type == "checkbox"

    assert not obj.value

    for each in text_element_attributes:
        assert not hasattr(obj, each)
