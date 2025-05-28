# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_fill(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "adobe_mode", "test_fill.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream, adobe_mode=True).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_dropdown_two(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "adobe_mode", "dropdown", "dropdown_two.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_dropdown, adobe_mode=True).fill(
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


def test_fill_sejda_complex(sejda_template_complex, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "adobe_mode", "paragraph", "sample_filled_sejda_complex.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template_complex, adobe_mode=True).fill(
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
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_issue_613(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "adobe_mode", "issues", "613_expected.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(pdf_samples, "scenario", "issues", "613.pdf"), adobe_mode=True
        ).fill(
            {
                "301 Full name": "John Smith",
                "301 Address Street": "1234 road number 6",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_sample_template_libary(pdf_samples, image_samples, request):
    expected_path = os.path.join(
        pdf_samples, "adobe_mode", "test_sample_template_libary.pdf"
    )

    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"), adobe_mode=True)
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
            .create_widget(
                widget_type="image",
                name="new_image_widget",
                page_number=1,
                x=300,
                y=200,
            )
            .create_widget(
                widget_type="signature",
                name="new_signature_wiget",
                page_number=1,
                x=300,
                y=400,
            )
            .fill(
                {
                    "new_text_field_widget": "test text",
                    "new_checkbox_widget": True,
                    "new_radio_group": 1,
                    "new_dropdown_widget": 2,
                    "new_image_widget": os.path.join(image_samples, "sample_image.jpg"),
                    "new_signature_wiget": os.path.join(
                        image_samples, "sample_signature.png"
                    ),
                },
            )
        )

        obj.widgets["new_text_field_widget"].font_color = (1, 0, 0)
        obj.widgets["new_text_field_widget"].alignment = 2
        obj.widgets["new_checkbox_widget"].size = 40
        obj.widgets["new_radio_group"].size = 50

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
