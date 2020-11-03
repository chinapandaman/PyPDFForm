# -*- coding: utf-8 -*-

import os

import pytest
from PyPDFForm import (InvalidFormDataError, InvalidModeError,
                       InvalidTemplateError, PyPDFForm)


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples")


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
