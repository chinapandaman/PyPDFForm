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
    expected_path = os.path.join(pdf_samples, "dropdown", "test_dropdown_one.pdf")
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

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_one_flatten(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_dropdown_one_flatten.pdf"
    )
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
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_two(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "dropdown", "test_dropdown_two.pdf")
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

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_two_flatten(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_dropdown_two_flatten.pdf"
    )
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
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_three(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "dropdown", "test_dropdown_three.pdf")
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

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_three_flatten(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_dropdown_three_flatten.pdf"
    )
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
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_four(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "dropdown", "test_dropdown_four.pdf")
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

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_four_flatten(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_dropdown_four_flatten.pdf"
    )
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
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_alignment(dropdown_alignment, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "dropdown", "test_dropdown_alignment.pdf")
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
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected


def test_dropdown_alignment_flatten(dropdown_alignment, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_dropdown_alignment_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(dropdown_alignment).fill(
            {
                "dropdown_left": 0,
                "dropdown_center": 1,
                "dropdown_right": 2,
            },
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        if os.name != "nt":
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected


def test_dropdown_alignment_flatten_then_unflatten(
    dropdown_alignment, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_dropdown_alignment_flatten_then_unflatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(dropdown_alignment).fill(
            {
                "dropdown_left": 0,
                "dropdown_center": 1,
                "dropdown_right": 2,
            },
            flatten=True,
        )
        obj.widgets["dropdown_center"].readonly = False

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        if os.name != "nt":
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected


def test_dropdown_alignment_sejda(dropdown_alignment_sejda, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_dropdown_alignment_sejda.pdf"
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

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_alignment_sejda_flatten(
    dropdown_alignment_sejda, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_dropdown_alignment_sejda_flatten.pdf"
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
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_alignment_sejda_flatten_then_unflatten(
    dropdown_alignment_sejda, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples,
        "dropdown",
        "test_dropdown_alignment_sejda_flatten_then_unflatten.pdf",
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
            flatten=True,
        )
        obj.widgets["dropdown_center"].readonly = False

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_change_dropdown_choices(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_change_dropdown_choices.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_dropdown)
        obj.widgets["dropdown_1"].choices = ["", "apple", "banana", "cherry", "dates"]

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_change_dropdown_choices_with_export_values(
    sample_template_with_dropdown, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_change_dropdown_choices_with_export_values.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_dropdown, adobe_mode=True)
        obj.widgets["dropdown_1"].choices = [
            ("apple_export", "apple"),
            ("banana_export", "banana"),
        ]

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
