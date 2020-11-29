# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import PyPDFForm


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


@pytest.fixture
def comparing_size():
    return 4095


def test_addition_operator_3_times(
    template_stream, image_stream, pdf_samples, comparing_size
):
    with open(os.path.join(pdf_samples, "sample_added_3_copies.pdf"), "rb+") as f:
        result = PyPDFForm()

        for i in range(3):
            obj = (
                PyPDFForm(template_stream)
                .fill(
                    {
                        "test": "{}_test_1".format(i),
                        "check": True,
                        "test_2": "{}_test_2".format(i),
                        "check_2": False,
                        "test_3": "{}_test_3".format(i),
                        "check_3": True,
                    },
                )
                .draw_image(image_stream, i + 1, 100, 100, 400, 225, 0)
            )

            result = result + obj

        expected = f.read()

        assert result.stream[:comparing_size] == expected[:comparing_size]


def test_addition_assignment_operator_3_times(
    template_stream, image_stream, pdf_samples, comparing_size
):
    with open(os.path.join(pdf_samples, "sample_added_3_copies.pdf"), "rb+") as f:
        result = PyPDFForm()

        for i in range(3):
            obj = (
                PyPDFForm(template_stream)
                .fill(
                    {
                        "test": "{}_test_1".format(i),
                        "check": True,
                        "test_2": "{}_test_2".format(i),
                        "check_2": False,
                        "test_3": "{}_test_3".format(i),
                        "check_3": True,
                    },
                )
                .draw_image(image_stream, i + 1, 100, 100, 400, 225, 0)
            )

            result += obj

        expected = f.read()

        assert str(result.stream)[:comparing_size] == str(expected)[:comparing_size]
