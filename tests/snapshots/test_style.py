# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_update_radio_key(template_with_radiobutton_stream, expect_pdf):
    obj = PdfWrapper(template_with_radiobutton_stream)
    obj.update_widget_key("radio_3", "RADIO")
    obj.commit_widget_key_updates()
    obj.fill({"RADIO": 0})

    expect_pdf(obj.read())


def test_update_sejda_key(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)
    obj.update_widget_key("year", "YEAR")
    obj.update_widget_key("at_future_date", "FUTURE_DATE")
    obj.update_widget_key("purchase_option", "PURCHASE_OPTION")
    obj.update_widget_key("buyer_signed_date", "BUYER_SIGNED_DATE")
    obj.commit_widget_key_updates()
    obj.fill(
        {
            "YEAR": "12",
            "FUTURE_DATE": True,
            "PURCHASE_OPTION": 1,
            "BUYER_SIGNED_DATE": "2012-01-01",
        }
    )

    expect_pdf(obj.read())


def test_hidden_text_check(template_stream, expect_pdf):
    obj = PdfWrapper(template_stream)
    obj.widgets["test"].hidden = True
    obj.widgets["check_2"].hidden = True

    expect_pdf(obj.read())


def test_hidden_radio(template_with_radiobutton_stream, expect_pdf):
    obj = PdfWrapper(template_with_radiobutton_stream)
    obj.widgets["radio_2"].hidden = True

    expect_pdf(obj.read())


def test_hidden_sejda(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)
    obj.widgets["buyer_name"].hidden = True
    obj.widgets["purchase_option"].hidden = True
    obj.widgets["at_future_date"].hidden = True

    expect_pdf(obj.read())


def test_set_text_field_font_sejda(font_samples, sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template).register_font(
        "new_font", os.path.join(font_samples, "LiberationSerif-Italic.ttf")
    )
    obj.register_font(
        "new_font_2", os.path.join(font_samples, "LiberationSerif-Bold.ttf")
    )
    obj.widgets["buyer_name"].font = "new_font_2"

    expect_pdf(obj.read())


def test_set_text_field_font_size_sejda(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)
    obj.widgets["buyer_name"].font_size = 30

    expect_pdf(obj.read())


def test_set_text_field_font_color_sejda(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)
    obj.widgets["buyer_name"].font_color = (1, 0, 0)

    expect_pdf(obj.read())


def test_set_text_field_alignment_sejda(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)
    obj.widgets["buyer_name"].alignment = 2

    expect_pdf(obj.read())


def test_set_text_field_max_length_sejda(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)
    obj.widgets["buyer_name"].max_length = 2

    expect_pdf(obj.read())


def test_set_text_field_comb_sejda(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)
    obj.widgets["buyer_name"].max_length = 2
    obj.widgets["buyer_name"].comb = True

    expect_pdf(obj.read())


def test_set_text_field_multiline_sejda(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)
    obj.widgets["buyer_name"].multiline = True

    expect_pdf(obj.read())


def test_set_checkbox_size_sejda(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)
    obj.widgets["date_of_this_bill"].size = 30

    expect_pdf(obj.read())


def test_set_radio_size(template_with_radiobutton_stream, expect_pdf):
    obj = PdfWrapper(template_with_radiobutton_stream)
    obj.widgets["radio_1"].size = 40

    expect_pdf(obj.read())


def test_set_radio_size_sejda(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)
    obj.widgets["purchase_option"].size = 40

    expect_pdf(obj.read())


def test_set_dropdown_font_sejda(
    dropdown_alignment_sejda, sample_font_stream, expect_pdf
):
    obj = PdfWrapper(dropdown_alignment_sejda)
    obj.register_font("new_font", sample_font_stream)
    obj.widgets["dropdown_left"].font = "new_font"

    expect_pdf(obj.read())


def test_set_dropdown_font_size_sejda(dropdown_alignment_sejda, expect_pdf):
    obj = PdfWrapper(dropdown_alignment_sejda)
    obj.widgets["dropdown_left"].font_size = 30

    expect_pdf(obj.read())


def test_set_dropdown_font_color_sejda(dropdown_alignment_sejda, expect_pdf):
    obj = PdfWrapper(dropdown_alignment_sejda)
    obj.widgets["dropdown_left"].font_color = (1, 0, 0)

    expect_pdf(obj.read())


def test_set_text_field_required_sejda(sejda_template, expect_pdf):
    obj = PdfWrapper(sejda_template)
    obj.widgets["buyer_address"].required = True

    expect_pdf(obj.read())
