# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm.legacy import PyPDFForm
from PyPDFForm.legacy.exceptions import (InvalidCoordinateError,
                                         InvalidEditableParameterError,
                                         InvalidFontColorError,
                                         InvalidFontSizeError,
                                         InvalidFormDataError,
                                         InvalidImageDimensionError,
                                         InvalidImageError,
                                         InvalidImageRotationAngleError,
                                         InvalidModeError,
                                         InvalidPageNumberError,
                                         InvalidTemplateError,
                                         InvalidTextError,
                                         InvalidTextOffsetError,
                                         InvalidWrapLengthError)


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "../..", "..", "pdf_samples")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def image_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_image.jpg"), "rb+") as f:
        return f.read()


def test_invalid_template_error():
    try:
        PyPDFForm(b"BAD_TEMPLATE").fill({})
        assert False
    except InvalidTemplateError:
        assert True


def test_invalid_form_data_error(template_stream):
    try:
        PyPDFForm(template_stream).fill("NOT_A_DICT")
        assert False
    except InvalidFormDataError:
        assert True


def test_invalid_mode_error(template_stream):
    try:
        PyPDFForm(template_stream, simple_mode=1).fill({})
        assert False
    except InvalidModeError:
        assert True


def test_invalid_font_size_error(template_stream):
    obj = PyPDFForm(template_stream, simple_mode=False)

    try:
        obj.fill({}, font_size="12")
        assert False
    except InvalidFontSizeError:
        assert True

    try:
        obj.elements["test"].font_size = "50"
        obj.fill({})
        assert False
    except InvalidFontSizeError:
        assert True


def test_invalid_font_color_error(template_stream):
    obj = PyPDFForm(template_stream, simple_mode=False)

    try:
        obj.fill({}, font_color=1)
        assert False
    except InvalidFontColorError:
        assert True

    try:
        obj.elements["test"].font_color = ("1", 0, 0)
        obj.fill({})
        assert False
    except InvalidFontColorError:
        assert True


def test_invalid_wrap_length_error(template_stream):
    obj = PyPDFForm(template_stream, simple_mode=False)

    try:
        obj.fill({}, text_wrap_length="100")
        assert False
    except InvalidWrapLengthError:
        assert True

    try:
        obj.elements["test"].text_wrap_length = "100"
        obj.fill({})
    except InvalidWrapLengthError:
        assert True


def test_invalid_image_error(template_stream):
    try:
        PyPDFForm(template_stream).draw_image(b"BAD_IMAGE", 1, 100, 100, 400, 225)
        assert False
    except InvalidImageError:
        assert True


def test_invalid_page_number_error(template_stream, image_stream):
    try:
        PyPDFForm(template_stream).draw_image(image_stream, 1.1, 100, 100, 400, 225)
        assert False
    except InvalidPageNumberError:
        assert True


def test_invalid_image_coordinate_error(template_stream, image_stream):
    try:
        PyPDFForm(template_stream).draw_image(image_stream, 1, "100", 100, 400, 225)
        assert False
    except InvalidCoordinateError:
        assert True

    try:
        PyPDFForm(template_stream).draw_image(image_stream, 1, 100, "100", 400, 225)
        assert False
    except InvalidCoordinateError:
        assert True


def test_invalid_image_dimension_error(template_stream, image_stream):
    try:
        PyPDFForm(template_stream).draw_image(image_stream, 1, 100, 100, "400", 225)
        assert False
    except InvalidImageDimensionError:
        assert True

    try:
        PyPDFForm(template_stream).draw_image(image_stream, 1, 100, 100, 400, "225")
        assert False
    except InvalidImageDimensionError:
        assert True


def test_invalid_image_rotation_angle_error(template_stream, image_stream):
    try:
        PyPDFForm(template_stream).draw_image(image_stream, 1, 100, 100, 400, 225, "90")
        assert False
    except InvalidImageRotationAngleError:
        assert True


def test_invalid_text_offset_error(template_stream):
    obj = PyPDFForm(template_stream, simple_mode=False)

    try:
        obj.fill({}, text_x_offset="100", text_y_offset=100)
        assert False
    except InvalidTextOffsetError:
        assert True

    try:
        obj.fill({}, text_x_offset=100, text_y_offset="100")
        assert False
    except InvalidTextOffsetError:
        assert True

    try:
        obj.elements["test"].text_x_offset = "100"
        obj.fill({})
        assert False
    except InvalidTextOffsetError:
        assert True

    try:
        obj.elements["test"].text_y_offset = "100"
        obj.fill({})
        assert False
    except InvalidTextOffsetError:
        assert True


def test_invalid_editable_parameter_error(template_stream):
    try:
        PyPDFForm(template_stream, simple_mode=True).fill({}, editable=1)
        assert False
    except InvalidEditableParameterError:
        assert True


def test_invalid_text_error(template_stream):
    try:
        PyPDFForm(template_stream, simple_mode=True).draw_text(1, 1, 0, 0)
        assert False
    except InvalidTextError:
        assert True
