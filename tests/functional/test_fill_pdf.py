# -*- coding: utf-8 -*-

import os

import pytest
from PyPDFForm import PyPDFForm


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def comparing_size():
    return 32767


def test_fill_simple_mode(template_stream, pdf_samples, comparing_size):
    with open(os.path.join(pdf_samples, "sample_filled_simple_mode.pdf"), "rb+") as f:
        obj = PyPDFForm().fill(
            template_stream,
            {
                "test": "test_1",
                "check": True,
                "test_2": "test_2",
                "check_2": False,
                "test_3": "test_3",
                "check_3": True,
            },
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream[:comparing_size] == expected[:comparing_size]


def test_fill_font_20(template_stream, pdf_samples, comparing_size):
    with open(os.path.join(pdf_samples, "sample_filled_font_20.pdf"), "rb+") as f:
        obj = PyPDFForm().fill(
            template_stream,
            {
                "test": "test_1",
                "check": True,
                "test_2": "test_2",
                "check_2": False,
                "test_3": "test_3",
                "check_3": True,
            },
            simple_mode=False,
            font_size=20,
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream[:comparing_size] == expected[:comparing_size]
