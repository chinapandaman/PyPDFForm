# -*- coding: utf-8 -*-

import os

from PyPDFForm import PyPDFForm


def test_generate_schema(sample_template_with_dropdown):
    schema = PyPDFForm(sample_template_with_dropdown).generate_schema()

    for key, value in schema["properties"].items():
        if key == "dropdown_1":
            assert value["maximum"] == 3


def test_dropdown_not_specified(sample_template_with_dropdown):
    assert (
        PyPDFForm(sample_template_with_dropdown)
        .fill(
            {
                "test_1": "test_1",
                "test_2": "test_2",
                "test_3": "test_3",
                "check_1": True,
                "check_2": True,
                "check_3": True,
                "radio_1": 1,
            }
        )
        .read()
    )


def test_dropdown_one(sample_template_with_dropdown, pdf_samples):
    with open(os.path.join(pdf_samples, "dropdown", "dropdown_one.pdf"), "rb+") as f:
        obj = PyPDFForm(sample_template_with_dropdown).fill(
            {
                "test_1": "test_1",
                "test_2": "test_2",
                "test_3": "test_3",
                "check_1": True,
                "check_2": True,
                "check_3": True,
                "radio_1": 1,
                "dropdown_1": 0,
            },
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_dropdown_two(sample_template_with_dropdown, pdf_samples):
    with open(os.path.join(pdf_samples, "dropdown", "dropdown_two.pdf"), "rb+") as f:
        obj = PyPDFForm(sample_template_with_dropdown).fill(
            {
                "test_1": "test_1",
                "test_2": "test_2",
                "test_3": "test_3",
                "check_1": True,
                "check_2": True,
                "check_3": True,
                "radio_1": 1,
                "dropdown_1": 1,
            },
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_dropdown_three(sample_template_with_dropdown, pdf_samples):
    with open(os.path.join(pdf_samples, "dropdown", "dropdown_three.pdf"), "rb+") as f:
        obj = PyPDFForm(sample_template_with_dropdown).fill(
            {
                "test_1": "test_1",
                "test_2": "test_2",
                "test_3": "test_3",
                "check_1": True,
                "check_2": True,
                "check_3": True,
                "radio_1": 1,
                "dropdown_1": 2,
            },
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_dropdown_four(sample_template_with_dropdown, pdf_samples):
    with open(os.path.join(pdf_samples, "dropdown", "dropdown_four.pdf"), "rb+") as f:
        obj = PyPDFForm(sample_template_with_dropdown).fill(
            {
                "test_1": "test_1",
                "test_2": "test_2",
                "test_3": "test_3",
                "check_1": True,
                "check_2": True,
                "check_3": True,
                "radio_1": 1,
                "dropdown_1": 3,
            },
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected
