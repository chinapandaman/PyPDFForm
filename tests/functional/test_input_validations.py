# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm.middleware.exceptions.input import (
    InvalidEditableParameterError, InvalidFormDataError, InvalidModeError)
from PyPDFForm.middleware.wrapper import PyPDFForm


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "v2")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
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
