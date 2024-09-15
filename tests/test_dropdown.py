# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_schema(sample_template_with_dropdown):
    obj = PdfWrapper(sample_template_with_dropdown)

    for key, value in obj.schema["properties"].items():
        if key == "dropdown_1":
            assert value["maximum"] == 3

    assert obj.sample_data["dropdown_1"] == 3


def test_dropdown_not_specified(sample_template_with_dropdown):
    assert (
        PdfWrapper(sample_template_with_dropdown)
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
    expected_path = os.path.join(pdf_samples, "dropdown", "dropdown_one.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_dropdown).fill(
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

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_dropdown_two(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "dropdown", "dropdown_two.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_dropdown).fill(
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

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_dropdown_three(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "dropdown", "dropdown_three.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_dropdown).fill(
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

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_dropdown_four(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "dropdown", "dropdown_four.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_dropdown).fill(
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

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_dropdown_alignment(dropdown_alignment, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "dropdown_alignment_expected.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(dropdown_alignment).fill(
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
            assert len(obj.stream) == len(expected)
            assert obj.stream == expected


def test_dropdown_alignment_sejda(dropdown_alignment_sejda, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "dropdown_alignment_sejda_expected.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(dropdown_alignment_sejda).fill(
            {
                "dropdown_left": 0,
                "dropdown_center": 1,
                "dropdown_right": 2,
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected
