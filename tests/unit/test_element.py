# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm.middleware.constants import Text as TextConstants
from PyPDFForm.middleware.element import Element, ElementType
from PyPDFForm.middleware.exceptions.element import (InvalidElementNameError,
                                                     InvalidElementTypeError,
                                                     InvalidElementValueError,
                                                     InvalidFontColorError,
                                                     InvalidFontError,
                                                     InvalidFontSizeError,
                                                     InvalidTextOffsetError,
                                                     InvalidWrapLengthError)


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "v2")


@pytest.fixture
def text_element_attributes():
    return [
        "font",
        "font_size",
        "font_color",
        "text_x_offset",
        "text_y_offset",
        "text_wrap_length",
    ]


@pytest.fixture
def text_element():
    return Element("foo", ElementType.text)


@pytest.fixture
def checkbox_element():
    return Element("foo", ElementType.checkbox)


@pytest.fixture
def radiobutton_element():
    return Element("foo", ElementType.radio)


def test_constructing_text_element(text_element, text_element_attributes):
    obj = text_element

    assert obj.name == "foo"
    assert obj.type == ElementType.text

    assert not obj.value

    for each in text_element_attributes:
        assert hasattr(obj, each)


def test_constructing_checkboxes_element(checkbox_element, text_element_attributes):
    obj = checkbox_element

    assert obj.name == "foo"
    assert obj.type == ElementType.checkbox

    assert not obj.value

    for each in text_element_attributes:
        assert not hasattr(obj, each)


def test_set_value(text_element, checkbox_element):
    text_element.value = "bar"
    assert text_element.value == "bar"

    checkbox_element.value = False
    assert checkbox_element.value is not None
    assert not checkbox_element.value


def test_validate_text_attributes(text_element):
    text_element.font = 0

    try:
        text_element.validate_text_attributes()
        assert False
    except InvalidFontError:
        assert True

    text_element.font = "bad_font"

    try:
        text_element.validate_text_attributes()
        assert False
    except InvalidFontError:
        assert True

    text_element.font = TextConstants().global_font

    text_element.font_size = ""

    try:
        text_element.validate_text_attributes()
        assert False
    except InvalidFontSizeError:
        assert True

    text_element.font_size = 12.5

    text_element.font_color = ""

    try:
        text_element.validate_text_attributes()
        assert False
    except InvalidFontColorError:
        assert True

    text_element.font_color = (1, 0, 0)

    text_element.text_x_offset = ""

    try:
        text_element.validate_text_attributes()
        assert False
    except InvalidTextOffsetError:
        assert True

    text_element.text_x_offset = 100

    text_element.text_y_offset = ""

    try:
        text_element.validate_text_attributes()
        assert False
    except InvalidTextOffsetError:
        assert True

    text_element.text_y_offset = 100

    text_element.text_wrap_length = ""

    try:
        text_element.validate_text_attributes()
        assert False
    except InvalidWrapLengthError:
        assert True

    text_element.text_wrap_length = 100.5

    try:
        text_element.validate_text_attributes()
        assert False
    except InvalidWrapLengthError:
        assert True

    text_element.text_wrap_length = 50

    text_element.validate_text_attributes()
    assert True


def test_setting_invalid_value(
    text_element, checkbox_element, radiobutton_element
):
    text_element.value = 0

    try:
        text_element.validate_value()
        assert False
    except InvalidElementValueError:
        assert True

    text_element.value = "foo"
    text_element.validate_value()

    checkbox_element.value = ""

    try:
        checkbox_element.validate_value()
        assert False
    except InvalidElementValueError:
        assert True

    checkbox_element.value = False
    checkbox_element.validate_value()

    radiobutton_element.value = "0"

    try:
        radiobutton_element.validate_value()
        assert False
    except InvalidElementValueError:
        assert True

    radiobutton_element.value = 0
    radiobutton_element.validate_value()

    assert True


def test_invalid_constants(text_element):
    text_element._name = 1

    try:
        text_element.validate_constants()
        assert False
    except InvalidElementNameError:
        assert True

    text_element._name = "foo"
    text_element._type = "text"

    try:
        text_element.validate_constants()
        assert False
    except InvalidElementTypeError:
        assert True
