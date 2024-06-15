# -*- coding: utf-8 -*-

import os

from PyPDFForm import FormWrapper


def test_dropdown_one(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "adobe_mode", "dropdown", "dropdown_one.pdf"
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
                "dropdown_1": 0,
            },
            adobe_mode=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_fill_sejda_complex(sejda_template_complex, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "adobe_mode", "paragraph", "sample_filled_sejda_complex.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sejda_template_complex).fill(
            {
                "checkbox": True,
                "radio": 0,
                "dropdown_font_auto_left": 0,
                "dropdown_font_auto_center": 1,
                "dropdown_font_auto_right": 2,
                "dropdown_font_ten_left": 0,
                "dropdown_font_ten_center": 1,
                "dropdown_font_ten_right": 2,
                "paragraph_font_auto_left": "paragraph_font_auto_left",
                "paragraph_font_auto_center": "paragraph_font_auto_center",
                "paragraph_font_auto_right": "paragraph_font_auto_right",
                "paragraph_font_ten_left": "paragraph_font_ten_left",
                "paragraph_font_ten_center": "paragraph_font_ten_center",
                "paragraph_font_ten_right": "paragraph_font_ten_right",
                "text__font_auto_left": "test text",
                "text_font_auto_center": "test text",
                "text_font_auto_right": "test text",
                "text_font_ten_left": "text_font_ten_left",
                "text_font_ten_center": "text_font_ten_center",
                "text_font_ten_right": "text_font_ten_right",
            },
            adobe_mode=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_issue_613(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "adobe_mode", "issues", "613_expected.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(
            os.path.join(pdf_samples, "scenario", "issues", "613.pdf")
        ).fill(
            {
                "301 Full name": "John Smith",
                "301 Address Street": "1234 road number 6",
            },
            adobe_mode=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected
