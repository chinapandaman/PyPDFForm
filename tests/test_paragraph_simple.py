# -*- coding: utf-8 -*-
# pylint: disable=line-too-long

import os

from PyPDFForm import FormWrapper


def test_paragraph_y_coordinate(sample_template_with_paragraph, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "paragraph", "test_paragraph_y_coordinate.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_paragraph).fill(
            {"paragraph_1": "test paragraph"}
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_paragraph_auto_wrap(sample_template_with_paragraph, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "paragraph", "test_paragraph_auto_wrap.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_paragraph).fill(
            {
                "paragraph_1": "t xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx t"
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_paragraph_auto_font(
    sample_template_with_paragraph_auto_font, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "simple", "paragraph", "test_paragraph_auto_font.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_paragraph_auto_font).fill(
            {"paragraph": "test paragraph"}
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_paragraph_auto_font_auto_wrap(
    sample_template_with_paragraph_auto_font, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "simple", "paragraph", "test_paragraph_auto_font_auto_wrap.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_paragraph_auto_font).fill(
            {
                "paragraph": "t xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx t"
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_paragraph_complex(sample_template_paragraph_complex, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "paragraph", "test_paragraph_complex.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_paragraph_complex).fill(
            {
                "paragraph_font_auto_left": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                "paragraph_font_auto_right": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                "paragraph_font_auto_center": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                "paragraph_font_ten_left": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                "paragraph_font_ten_right": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                "paragraph_font_ten_center": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected
