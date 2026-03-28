# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import Fields, PdfWrapper, RawElements


@pytest.mark.posix_only
def test_register_font_no_form_fields(pdf_samples, sample_font_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_register_font_no_form_fields.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
        obj.register_font("new_font", sample_font_stream).create_field(
            Fields.TextField(name="foo", page_number=1, x=100, y=100, font="new_font")
        )
        obj.draw([RawElements.RawText("foo", 1, 200, 200, font="new_font")])

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_register_multiple_fonts(pdf_samples, font_samples, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_register_multiple_fonts.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
        obj.register_font("foo", os.path.join(font_samples, "LiberationSerif-Bold.ttf"))
        obj.register_font(
            "bar", os.path.join(font_samples, "LiberationSerif-Italic.ttf")
        )
        obj.create_field(
            Fields.TextField(name="foo", page_number=1, x=100, y=100, font="foo")
        )
        obj.create_field(
            Fields.TextField(name="bar", page_number=1, x=100, y=200, font="bar")
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_radio_size(pdf_samples, template_with_radiobutton_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_radio_size.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_with_radiobutton_stream)
        obj.widgets["radio_1"].size = 40

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_set_dropdown_font_sejda(
    pdf_samples, dropdown_alignment_sejda, sample_font_stream, request
):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_dropdown_font_sejda.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(dropdown_alignment_sejda)
        obj.register_font("new_font", sample_font_stream)
        obj.widgets["dropdown_left"].font = "new_font"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_dropdown_font_size_sejda(pdf_samples, dropdown_alignment_sejda, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_dropdown_font_size_sejda.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(dropdown_alignment_sejda)
        obj.widgets["dropdown_left"].font_size = 30

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_dropdown_font_color_sejda(pdf_samples, dropdown_alignment_sejda, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_dropdown_font_color_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(dropdown_alignment_sejda)
        obj.widgets["dropdown_left"].font_color = (1, 0, 0)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
