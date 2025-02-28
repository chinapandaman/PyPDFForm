# -*- coding: utf-8 -*-

import os

from PyPDFForm import FormWrapper, PdfWrapper
from PyPDFForm.constants import UNIQUE_SUFFIX_LENGTH, T, V
from PyPDFForm.template import get_widgets_by_page


def test_fill(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "simple", "sample_filled.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(template_stream).fill(data_dict)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_radiobutton(pdf_samples, template_with_radiobutton_stream, request):
    expected_path = os.path.join(pdf_samples, "simple", "sample_filled_radiobutton.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(template_with_radiobutton_stream).fill(
            {
                "radio_1": 0,
                "radio_2": 1,
                "radio_3": 2,
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_fill_sejda_and_read(pdf_samples, sejda_template, sejda_data, request):
    expected_path = os.path.join(pdf_samples, "simple", "sample_filled_sejda.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sejda_template).fill(sejda_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_fill_right_aligned(
    sample_template_with_right_aligned_text_field, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "simple", "sample_filled_right_aligned.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_right_aligned_text_field).fill(
            {
                "name": "Hans Mustermann",
                "fulladdress": "Musterstr. 12, 82903 Musterdorf, Musterland",
                "advisorname": "Karl Test",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_fill_font_color(sample_template_with_font_colors, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "test_fill_font_color.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_font_colors).fill(
            {
                "red_12": "red",
                "green_14": "green",
                "blue_16": "blue",
                "mixed_auto": "mixed",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        if os.name != "nt":
            assert len(obj.read()) == len(expected)
            assert obj.stream == expected


def test_fill_complex_fonts(sample_template_with_complex_fonts, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "test_fill_complex_fonts.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_complex_fonts).fill(
            {
                "Courier": "Test",
                "Courier-Bold": "Test",
                "Courier-BoldOblique": "Test",
                "Courier-Oblique": "Test",
                "Helvetica": "Test",
                "Helvetica-Bold": "Test",
                "Helvetica-BoldOblique": "Test",
                "Helvetica-Oblique": "Test",
                "Times-Bold": "Test",
                "Times-BoldItalic": "Test",
                "Times-Italic": "Test",
                "Times-Roman": "Test",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        if os.name != "nt":
            assert len(obj.read()) == len(expected)
            assert obj.stream == expected


def test_undo_checkbox(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "simple", "undo", "test_undo_checkbox.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(
            os.path.join(pdf_samples, "simple", "undo", "sample_template_filled.pdf")
        ).fill(
            {
                "check": False,
                "check_2": False,
                "check_3": False,
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_merging_unique_suffix(template_stream):
    result = PdfWrapper()

    for i in range(10):
        obj = PdfWrapper(
            FormWrapper(template_stream).fill({"test": f"value-{i}"}).read()
        )
        result += obj

    merged = PdfWrapper(result.read())

    for page, widgets in get_widgets_by_page(result.read()).items():
        for widget in widgets:
            assert widget[T] in merged.widgets
            if widget[T] == "test":
                assert widget[V] == "value-0"
            elif V in widget and "value-" in widget[V]:
                assert widget[V] == f"value-{page // 3}"
                assert widget[T].split("-")[0] == "test"
                assert len(widget[T].split("-")[1]) == UNIQUE_SUFFIX_LENGTH
