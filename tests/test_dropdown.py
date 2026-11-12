# -*- coding: utf-8 -*-

import os
from unittest.mock import patch

import pytest

from PyPDFForm import PdfWrapper


def test_schema(sample_template_with_dropdown):
    obj = PdfWrapper(sample_template_with_dropdown)

    for key, value in obj.schema["properties"].items():
        if key == "dropdown_1":
            for each in value["anyOf"]:
                if each["type"] == "integer":
                    assert each["maximum"] == 3

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


def test_dropdown_one_readonly(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_dropdown_one_readonly.pdf"
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
            readonly=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_alignment(dropdown_alignment, pdf_samples, request, assert_same_pdf):
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

        assert_same_pdf(obj.read(), expected)


def test_dropdown_alignment_readonly_then_editable(
    dropdown_alignment, pdf_samples, request, assert_same_pdf
):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_dropdown_alignment_readonly_then_editable.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(dropdown_alignment).fill(
            {
                "dropdown_left": 0,
                "dropdown_center": 1,
                "dropdown_right": 2,
            },
            readonly=True,
        )
        obj.widgets["dropdown_center"].readonly = False

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert_same_pdf(obj.read(), expected)


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


def test_dropdown_alignment_sejda_readonly(
    dropdown_alignment_sejda, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "dropdown", "test_dropdown_alignment_sejda_readonly.pdf"
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
            readonly=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_alignment_sejda_readonly_then_editable(
    dropdown_alignment_sejda, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples,
        "dropdown",
        "test_dropdown_alignment_sejda_readonly_then_editable.pdf",
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
            readonly=True,
        )
        obj.widgets["dropdown_center"].readonly = False

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_failed_fill_restores_dropdown(
    sample_template_with_dropdown, assert_widgets_match_output
):
    obj = PdfWrapper(sample_template_with_dropdown)
    original = obj.read()
    data = obj.data
    choices = obj.widgets["dropdown_1"].choices

    with (
        patch("PyPDFForm.lib.wrapper.fill", side_effect=RuntimeError),
        pytest.raises(RuntimeError),
    ):
        obj.fill({"test_1": "test_1", "dropdown_1": "new choice"})

    assert obj.data == data
    assert obj.widgets["dropdown_1"].choices == choices
    assert not any(widget.hooks_to_trigger for widget in obj.widgets.values())
    assert obj.read() == original
    assert_widgets_match_output(obj)
