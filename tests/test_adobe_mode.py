# -*- coding: utf-8 -*-

import os

from PyPDFForm import FormWrapper, PdfWrapper


def test_dropdown_two(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "adobe_mode", "dropdown", "dropdown_two.pdf"
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


def test_sample_template_libary(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "adobe_mode", "test_sample_template_libary.pdf"
    )
    template = (
        PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
        .create_widget(
            widget_type="text",
            name="new_text_field_widget",
            page_number=1,
            x=60,
            y=710,
        )
        .create_widget(
            widget_type="checkbox",
            name="new_checkbox_widget",
            page_number=1,
            x=100,
            y=600,
        )
        .create_widget(
            widget_type="radio",
            name="new_radio_group",
            page_number=1,
            x=[50, 100, 150],
            y=[50, 100, 150],
        )
        .create_widget(
            widget_type="dropdown",
            name="new_dropdown_widget",
            page_number=1,
            x=300,
            y=710,
            options=[
                "foo",
                "bar",
                "foobar",
            ],
        )
    )

    with open(expected_path, "rb+") as f:
        obj = FormWrapper(template.read()).fill(
            {
                "new_text_field_widget": "test text",
                "new_checkbox_widget": True,
                "new_radio_group": 1,
                "new_dropdown_widget": 2,
            },
            adobe_mode=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected
