# -*- coding: utf-8 -*-

from PyPDFForm.middleware.exceptions.input import (
    InvalidEditableParameterError, InvalidFormDataError, InvalidModeError)
from PyPDFForm.middleware.wrapper import PyPDFForm


def test_validate_constructor_inputs():
    bad_inputs = [b"", "True"]

    try:
        PyPDFForm(*bad_inputs)
        assert False
    except InvalidModeError:
        assert True


def test_validate_simple_fill_inputs():
    bad_inputs = ["not_dict", "True"]

    try:
        PyPDFForm().fill(*bad_inputs)
        assert False
    except InvalidFormDataError:
        assert True

    bad_inputs[0] = {}

    try:
        PyPDFForm().fill(*bad_inputs)
    except InvalidEditableParameterError:
        assert True
