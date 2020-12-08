# -*- coding: utf-8 -*-

import os

import pytest

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


def test_fill_simple_mode(template_stream, pdf_samples, data_dict):
    with open(os.path.join(pdf_samples, "sample_filled_simple_mode.pdf"), "rb+") as f:
        obj = PyPDFForm(template_stream).fill(
            data_dict,
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_simple_mode_editable(template_stream, pdf_samples, data_dict):
    with open(
        os.path.join(pdf_samples, "sample_filled_simple_mode_editable.pdf"), "rb+"
    ) as f:
        obj = PyPDFForm(template_stream).fill(
            data_dict,
            editable=True,
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected
