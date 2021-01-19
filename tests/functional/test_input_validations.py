# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import PyPDFForm
from PyPDFForm.middleware.constants import Text as TextConstants
from PyPDFForm.middleware.exceptions.element import (InvalidFontColorError,
                                                     InvalidFontSizeError,
                                                     InvalidTextOffsetError,
                                                     InvalidWrapLengthError, InvalidFontError)
from PyPDFForm.middleware.exceptions.input import (
    InvalidCoordinateError, InvalidEditableParameterError,
    InvalidFormDataError, InvalidImageDimensionError, InvalidImageError,
    InvalidImageRotationAngleError, InvalidModeError, InvalidPageNumberError,
    InvalidTextError, InvalidTTFFontError)
from PyPDFForm.middleware.exceptions.template import InvalidTemplateError


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "v2")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def image_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_image.jpg"), "rb+") as f:
        return f.read()


@pytest.fixture
def font_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "font_samples")


def test_validate_constructor_inputs(template_stream):
    bad_inputs = ["", "True", 1, "12", ("0", "0", "0"), "0", "0", "100"]

    try:
        PyPDFForm(*bad_inputs)
        assert False
    except InvalidTemplateError:
        assert True

    bad_inputs[0] = b"bad_stream"

    try:
        PyPDFForm(*bad_inputs)
        assert False
    except InvalidModeError:
        assert True

    bad_inputs[1] = False

    try:
        PyPDFForm(*bad_inputs)
        assert False
    except InvalidTemplateError:
        assert True

    bad_inputs[0] = template_stream

    try:
        PyPDFForm(*bad_inputs)
        assert False
    except InvalidFontError:
        assert True

    bad_inputs[2] = "bad_font"

    try:
        PyPDFForm(*bad_inputs)
        assert False
    except InvalidFontError:
        assert True

    bad_inputs[2] = TextConstants().global_font

    try:
        PyPDFForm(*bad_inputs)
        assert False
    except InvalidFontSizeError:
        assert True

    bad_inputs[3] = 12

    try:
        PyPDFForm(*bad_inputs)
        assert False
    except InvalidFontColorError:
        assert True

    bad_inputs[4] = (0, 0, 0)

    try:
        PyPDFForm(*bad_inputs)
        assert False
    except InvalidTextOffsetError:
        assert True

    bad_inputs[5] = 0

    try:
        PyPDFForm(*bad_inputs)
        assert False
    except InvalidTextOffsetError:
        assert True

    bad_inputs[6] = 0

    try:
        PyPDFForm(*bad_inputs)
        assert False
    except InvalidWrapLengthError:
        assert True

    bad_inputs[7] = 100
    bad_inputs[0] = b""
    obj = PyPDFForm(*bad_inputs)
    assert obj.elements == {}


def test_validate_addition_operator_inputs(template_stream):
    assert (PyPDFForm() + PyPDFForm(template_stream)).stream == template_stream
    assert (PyPDFForm(template_stream) + PyPDFForm()).stream == template_stream

    result = PyPDFForm(b"bad_stream")

    try:
        result += PyPDFForm(b"bad_stream")
        assert False
    except InvalidTemplateError:
        assert True

    result.stream = template_stream

    try:
        result += PyPDFForm(b"bad_stream")
        assert False
    except InvalidTemplateError:
        assert True

    result += PyPDFForm(template_stream)
    assert True


def test_validate_fill_inputs(template_stream):
    bad_inputs = ["not_dict"]

    try:
        PyPDFForm(template_stream, False).fill(*bad_inputs)
        assert False
    except InvalidFormDataError:
        assert True

    bad_inputs[0] = {0: "foo"}

    try:
        PyPDFForm(template_stream, False).fill(*bad_inputs)
        assert False
    except InvalidFormDataError:
        assert True

    bad_inputs[0] = {"foo": 0}

    try:
        PyPDFForm(template_stream, False).fill(*bad_inputs)
        assert False
    except InvalidFormDataError:
        assert True

    bad_inputs[0] = {"foo": "", "bar": True}

    PyPDFForm(template_stream, False).fill(*bad_inputs)
    assert True


def test_validate_simple_fill_inputs(template_stream):
    bad_inputs = ["not_dict", "True"]

    try:
        PyPDFForm(template_stream).fill(*bad_inputs)
        assert False
    except InvalidFormDataError:
        assert True

    bad_inputs[0] = {0: "foo"}

    try:
        PyPDFForm(template_stream).fill(*bad_inputs)
        assert False
    except InvalidFormDataError:
        assert True

    bad_inputs[0] = {"foo": 0}

    try:
        PyPDFForm(template_stream).fill(*bad_inputs)
        assert False
    except InvalidFormDataError:
        assert True

    bad_inputs[0] = {"foo": "", "bar": True}

    try:
        PyPDFForm(template_stream).fill(*bad_inputs)
    except InvalidEditableParameterError:
        assert True

    bad_inputs[1] = True
    PyPDFForm(template_stream).fill(*bad_inputs)
    assert True


def test_validate_draw_text_inputs(template_stream):
    bad_inputs = [1, "1", "300", "225", 1, "20", [1, 0, 0], "50", "50", "4"]

    try:
        obj = PyPDFForm(b"bad_stream")
        obj.draw_text(*bad_inputs)
        assert False
    except InvalidTemplateError:
        assert True

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidTextError:
        assert True

    bad_inputs[0] = "drawn_text"

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidPageNumberError:
        assert True

    bad_inputs[1] = 1

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidCoordinateError:
        assert True

    bad_inputs[2] = 300

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidCoordinateError:
        assert True

    bad_inputs[3] = 225

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidFontError:
        assert True

    bad_inputs[4] = "bad_font"

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidFontError:
        assert True

    bad_inputs[4] = TextConstants().global_font

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidFontSizeError:
        assert True

    bad_inputs[5] = 20

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidFontColorError:
        assert True

    bad_inputs[6] = (1, 0, 0)

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidTextOffsetError:
        assert True

    bad_inputs[7] = 50

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidTextOffsetError:
        assert True

    bad_inputs[8] = 50

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidWrapLengthError:
        assert True

    bad_inputs[9] = 4
    PyPDFForm(template_stream).draw_text(*bad_inputs)
    assert True


def test_validate_draw_image_inputs(template_stream, image_stream):
    bad_inputs = [b"", "1", "100", "100", "400", "225", "180"]

    try:
        obj = PyPDFForm(b"bad_stream")
        obj.draw_image(*bad_inputs)
        assert False
    except InvalidTemplateError:
        assert True

    try:
        PyPDFForm(template_stream).draw_image(*bad_inputs)
        assert False
    except InvalidImageRotationAngleError:
        assert True

    bad_inputs[6] = 180

    try:
        PyPDFForm(template_stream).draw_image(*bad_inputs)
        assert False
    except InvalidImageError:
        assert True

    bad_inputs[0] = image_stream

    try:
        PyPDFForm(template_stream).draw_image(*bad_inputs)
        assert False
    except InvalidPageNumberError:
        assert True

    bad_inputs[1] = 1

    try:
        PyPDFForm(template_stream).draw_image(*bad_inputs)
        assert False
    except InvalidCoordinateError:
        assert True

    bad_inputs[2] = 100

    try:
        PyPDFForm(template_stream).draw_image(*bad_inputs)
        assert False
    except InvalidCoordinateError:
        assert True

    bad_inputs[3] = 100

    try:
        PyPDFForm(template_stream).draw_image(*bad_inputs)
        assert False
    except InvalidImageDimensionError:
        assert True

    bad_inputs[4] = 400

    try:
        PyPDFForm(template_stream).draw_image(*bad_inputs)
        assert False
    except InvalidImageDimensionError:
        assert True

    bad_inputs[5] = 225

    PyPDFForm(template_stream).draw_image(*bad_inputs)
    assert True


def test_validate_register_font_inputs(font_samples):
    bad_inputs = [None, None]

    try:
        PyPDFForm.register_font(*bad_inputs)
        assert False
    except InvalidTTFFontError:
        assert True

    bad_inputs[0] = 1

    try:
        PyPDFForm.register_font(*bad_inputs)
        assert False
    except InvalidTTFFontError:
        assert True

    bad_inputs[0] = "LiberationSerifBold"

    try:
        PyPDFForm.register_font(*bad_inputs)
        assert False
    except InvalidTTFFontError:
        assert True

    bad_inputs[1] = "foo"

    try:
        PyPDFForm.register_font(*bad_inputs)
        assert False
    except InvalidTTFFontError:
        assert True

    bad_inputs[1] = b"foo"

    try:
        PyPDFForm.register_font(*bad_inputs)
        assert False
    except InvalidTTFFontError:
        assert True

    with open(os.path.join(font_samples, "LiberationSerif-Bold.ttf"), "rb+") as f:
        bad_inputs[1] = f.read()

        assert PyPDFForm.register_font(*bad_inputs)
