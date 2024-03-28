# -*- coding: utf-8 -*-

import os

from PyPDFForm import FormWrapper


def test_dropdown_not_specified(sample_template_with_dropdown):
    assert (
        FormWrapper(sample_template_with_dropdown)
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


def test_dropdown_one(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "dropdown", "dropdown_one.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_dropdown).fill(
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

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_dropdown_two(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "dropdown", "dropdown_two.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_dropdown).fill(
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

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_dropdown_two_flatten(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "simple", "dropdown", "dropdown_two_simple.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_dropdown).fill(
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
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_dropdown_three(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "simple", "dropdown", "dropdown_three.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_dropdown).fill(
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

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_dropdown_four(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "dropdown", "dropdown_four.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_dropdown).fill(
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

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_dropdown_alignment(dropdown_alignment, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "simple", "dropdown", "dropdown_alignment_expected.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(dropdown_alignment).fill(
            {
                "dropdown_left": 0,
                "dropdown_center": 1,
                "dropdown_right": 2,
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        if os.name != "nt":
            assert len(obj.read()) == len(expected)
            assert obj.stream == expected
