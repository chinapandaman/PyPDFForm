# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_register_font_no_form_fields(pdf_samples, sample_font_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_register_font_no_form_fields.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
        obj.register_font("new_font", sample_font_stream).create_widget(
            "text", "foo", 1, 100, 100, font="new_font"
        )
        obj.draw_text("foo", 1, 200, 200, font="new_font")

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_font(pdf_samples, font_samples, template_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_text_field_font.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font", os.path.join(font_samples, "LiberationSerif-BoldItalic.ttf")
        )
        obj.widgets["test"].font = "new_font"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_font_sejda(pdf_samples, font_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_font_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template).register_font(
            "new_font", os.path.join(font_samples, "LiberationSerif-Italic.ttf")
        )
        obj.register_font(
            "new_font_2", os.path.join(font_samples, "LiberationSerif-Bold.ttf")
        )
        obj.widgets["buyer_name"].font = "new_font_2"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_font_size(pdf_samples, template_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_text_field_font_size.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["test"].font_size = 30

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_font_size_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_font_size_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].font_size = 30

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_font_color(pdf_samples, template_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_text_field_font_color.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["test"].font_color = (1, 0, 0)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_font_color_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_font_color_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].font_color = (1, 0, 0)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_alignment(pdf_samples, template_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_text_field_alignment.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["test"].alignment = 2

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_alignment_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_alignment_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].alignment = 2

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_max_length(pdf_samples, template_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_text_field_max_length.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["test"].max_length = 2

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_max_length_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_max_length_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].max_length = 2

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_comb(pdf_samples, template_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_text_field_comb.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["test"].max_length = 2
        obj.widgets["test"].comb = True

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_comb_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_comb_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].max_length = 2
        obj.widgets["buyer_name"].comb = True

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_multiline(pdf_samples, template_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_text_field_multiline.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["test"].multiline = True

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_multiline_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_multiline_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].multiline = True

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_checkbox_size(pdf_samples, template_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_checkbox_size.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["check"].size = 30

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_checkbox_size_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_checkbox_size_sejda.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["date_of_this_bill"].size = 30

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


def test_set_radio_size_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_radio_size_sejda.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["purchase_option"].size = 40

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_dropdown_font(
    pdf_samples, sample_template_with_dropdown, sample_font_stream, request
):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_dropdown_font.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_dropdown)
        obj.register_font("new_font", sample_font_stream)
        obj.widgets["dropdown_1"].font = "new_font"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


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
