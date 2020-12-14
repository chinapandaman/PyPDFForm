# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm.middleware.exceptions.input import (
    InvalidCoordinateError, InvalidEditableParameterError,
    InvalidFormDataError, InvalidImageDimensionError, InvalidImageError,
    InvalidImageRotationAngleError, InvalidModeError, InvalidPageNumberError, InvalidTextError)
from PyPDFForm.middleware.exceptions.element import (
    InvalidFontSizeError, InvalidFontColorError, InvalidTextOffsetError, InvalidWrapLengthError,
)
from PyPDFForm.middleware.wrapper import PyPDFForm


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


def test_validate_constructor_inputs():
    bad_inputs = [b"", "True"]

    try:
        PyPDFForm(*bad_inputs)
        assert False
    except InvalidModeError:
        assert True


def test_validate_simple_fill_inputs(template_stream):
    bad_inputs = ["not_dict", "True"]

    try:
        PyPDFForm(template_stream).fill(*bad_inputs)
        assert False
    except InvalidFormDataError:
        assert True

    bad_inputs[0] = {}

    try:
        PyPDFForm(template_stream).fill(*bad_inputs)
    except InvalidEditableParameterError:
        assert True


def test_validate_draw_text_inputs(template_stream):
    bad_inputs = [1, "1", "300", "225", "20", [1, 0, 0], "50", "50", "4"]

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
    except InvalidFontSizeError:
        assert True

    bad_inputs[4] = 20

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidFontColorError:
        assert True

    bad_inputs[5] = (1, 0, 0)

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidTextOffsetError:
        assert True

    bad_inputs[6] = 50

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidTextOffsetError:
        assert True

    bad_inputs[7] = 50

    try:
        PyPDFForm(template_stream).draw_text(*bad_inputs)
        assert False
    except InvalidWrapLengthError:
        assert True

    bad_inputs[8] = 4
    PyPDFForm(template_stream).draw_text(*bad_inputs)
    assert True


def test_validate_draw_image_inputs(template_stream, image_stream):
    bad_inputs = [b"", "1", "100", "100", "400", "225", "180"]

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
