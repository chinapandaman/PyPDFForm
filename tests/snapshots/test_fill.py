# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_fill_readonly_then_editable(template_stream, data_dict, expect_pdf):
    obj = PdfWrapper(template_stream).fill(data_dict, readonly=True)
    obj.widgets["test_2"].readonly = False
    obj.widgets["check_3"].readonly = False
    # earlier reads don't change what a later one writes
    for _ in range(4):
        obj.read()

    expect_pdf(obj.read())


def test_fill_with_customized_widgets(
    template_stream, sample_font_stream, data_dict, expect_pdf
):
    obj = PdfWrapper(template_stream).register_font(
        "new_font",
        sample_font_stream,
    )
    obj.widgets["test"].font = "new_font"
    obj.widgets["test"].font_size = 20
    obj.widgets["test"].font_color = (1, 0, 0)
    obj.widgets["test_2"].font_color = (0, 1, 0)
    obj.fill(
        data_dict,
    )

    expect_pdf(obj.read())


def test_fill_with_customized_widgets_readonly(
    template_stream, sample_font_stream, data_dict, expect_pdf
):
    obj = PdfWrapper(template_stream).register_font(
        "new_font",
        sample_font_stream,
    )
    obj.widgets["test"].font = "new_font"
    obj.widgets["test"].font_size = 20
    obj.widgets["test"].font_color = (1, 0, 0)
    obj.widgets["test_2"].font_color = (0, 1, 0)
    obj.fill(
        data_dict,
        readonly=True,
    )

    expect_pdf(obj.read())


def test_fill_with_varied_int_values(template_stream, expect_pdf):
    obj = PdfWrapper(template_stream).fill(
        {
            "test": 100,
            "test_2": -250,
            "test_3": 0,
        }
    )

    expect_pdf(obj.read())


def test_fill_radiobutton_readonly(template_with_radiobutton_stream, expect_pdf):
    obj = PdfWrapper(template_with_radiobutton_stream).fill(
        {
            "radio_1": 0,
            "radio_2": 1,
            "radio_3": 2,
        },
        readonly=True,
    )

    expect_pdf(obj.read())


def test_fill_radiobutton_readonly_then_editable(
    template_with_radiobutton_stream, expect_pdf
):
    obj = PdfWrapper(template_with_radiobutton_stream).fill(
        {
            "radio_1": 0,
            "radio_2": 1,
            "radio_3": 2,
        },
        readonly=True,
    )
    obj.widgets["radio_2"].readonly = False

    expect_pdf(obj.read())


def test_fill_sejda(sejda_template, sejda_data, expect_pdf):
    obj = PdfWrapper(sejda_template).fill(sejda_data)

    expect_pdf(obj.read())


def test_fill_sejda_readonly(sejda_template, sejda_data, expect_pdf):
    obj = PdfWrapper(sejda_template).fill(
        sejda_data,
        readonly=True,
    )

    expect_pdf(obj.read())


def test_fill_sejda_readonly_then_editable(sejda_template, sejda_data, expect_pdf):
    obj = PdfWrapper(sejda_template).fill(
        sejda_data,
        readonly=True,
    )
    obj.widgets["buyer_name"].readonly = False
    obj.widgets["at_future_date"].readonly = False
    obj.widgets["purchase_option"].readonly = False

    expect_pdf(obj.read())


def test_fill_right_aligned(sample_template_with_right_aligned_text_field, expect_pdf):
    obj = PdfWrapper(sample_template_with_right_aligned_text_field).fill(
        {
            "name": "Hans Mustermann",
            "fulladdress": "Musterstr. 12, 82903 Musterdorf, Musterland",
            "advisorname": "Karl Test",
        },
    )

    expect_pdf(obj.read())


def test_fill_font_color(sample_template_with_font_colors, expect_pdf):
    obj = PdfWrapper(sample_template_with_font_colors).fill(
        {
            "red_12": "red",
            "green_14": "green",
            "blue_16": "blue",
            "mixed_auto": "mixed",
        },
    )

    expect_pdf(obj.read())


def test_fill_complex_fonts(sample_template_with_complex_fonts, expect_pdf):
    obj = PdfWrapper(sample_template_with_complex_fonts).fill(
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

    expect_pdf(obj.read())


def test_uncheck_checkbox(pdf_samples, expect_pdf):
    obj = PdfWrapper(os.path.join(pdf_samples, "sample_template_filled.pdf")).fill(
        {"check": False, "check_2": False, "check_3": False},
    )

    expect_pdf(obj.read())


def test_dropdown_one_readonly(sample_template_with_dropdown, expect_pdf):
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

    expect_pdf(obj.read())


def test_dropdown_alignment(dropdown_alignment, expect_pdf):
    obj = PdfWrapper(dropdown_alignment).fill(
        {
            "dropdown_left": 0,
            "dropdown_center": 1,
            "dropdown_right": 2,
        },
    )

    expect_pdf(obj.read())


def test_dropdown_alignment_readonly_then_editable(dropdown_alignment, expect_pdf):
    obj = PdfWrapper(dropdown_alignment).fill(
        {
            "dropdown_left": 0,
            "dropdown_center": 1,
            "dropdown_right": 2,
        },
        readonly=True,
    )
    obj.widgets["dropdown_center"].readonly = False

    expect_pdf(obj.read())


def test_dropdown_alignment_sejda(dropdown_alignment_sejda, expect_pdf):
    obj = PdfWrapper(dropdown_alignment_sejda).fill(
        {
            "dropdown_left": 0,
            "dropdown_center": 1,
            "dropdown_right": 2,
        },
    )

    expect_pdf(obj.read())


def test_dropdown_alignment_sejda_readonly(dropdown_alignment_sejda, expect_pdf):
    obj = PdfWrapper(dropdown_alignment_sejda).fill(
        {
            "dropdown_left": 0,
            "dropdown_center": 1,
            "dropdown_right": 2,
        },
        readonly=True,
    )

    expect_pdf(obj.read())


def test_dropdown_alignment_sejda_readonly_then_editable(
    dropdown_alignment_sejda, expect_pdf
):
    obj = PdfWrapper(dropdown_alignment_sejda).fill(
        {
            "dropdown_left": 0,
            "dropdown_center": 1,
            "dropdown_right": 2,
        },
        readonly=True,
    )
    obj.widgets["dropdown_center"].readonly = False

    expect_pdf(obj.read())


def test_fill_sejda_complex(sejda_template_complex, sejda_complex_data, expect_pdf):
    obj = PdfWrapper(sejda_template_complex).fill(sejda_complex_data)

    expect_pdf(obj.read())


def test_fill_sejda_complex_readonly(
    sejda_template_complex, sejda_complex_data, expect_pdf
):
    obj = PdfWrapper(sejda_template_complex).fill(
        sejda_complex_data,
        readonly=True,
    )

    expect_pdf(obj.read())


def test_paragraph_complex(sample_template_paragraph_complex, expect_pdf):
    obj = PdfWrapper(sample_template_paragraph_complex).fill(
        {
            "paragraph_font_auto_left": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "paragraph_font_auto_right": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "paragraph_font_auto_center": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "paragraph_font_ten_left": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "paragraph_font_ten_right": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "paragraph_font_ten_center": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
        }
    )

    expect_pdf(obj.read())


def test_paragraph_max_length(sample_template_with_paragraph_max_length, expect_pdf):
    obj = PdfWrapper(sample_template_with_paragraph_max_length).fill(
        {
            "paragraph": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
        }
    )

    expect_pdf(obj.read())


def test_fill_max_length_text_field_all_chars(
    sample_template_with_max_length_text_field,
    expect_pdf,
):
    obj = PdfWrapper(sample_template_with_max_length_text_field).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXXXXXXXXX",
            "Awesomeness": True,
            "Gender": 0,
        }
    )

    expect_pdf(obj.read())


def test_fill_comb_text_field_all_chars(
    sample_template_with_comb_text_field, expect_pdf
):
    obj = PdfWrapper(sample_template_with_comb_text_field).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXXXXXXXXX",
            "Awesomeness": True,
            "Gender": 0,
        }
    )

    expect_pdf(obj.read())


def test_fill_comb_text_field_all_chars_readonly(
    sample_template_with_comb_text_field, expect_pdf
):
    obj = PdfWrapper(sample_template_with_comb_text_field).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXXXXXXXXX",
            "Awesomeness": True,
            "Gender": 0,
        },
        readonly=True,
    )

    expect_pdf(obj.read())


def test_fill_comb_text_field_void(sample_template_with_comb_text_field, expect_pdf):
    obj = PdfWrapper(sample_template_with_comb_text_field).fill({})

    expect_pdf(obj.read())


def test_fill_comb_text_field_even_chars_right_aligned(
    sample_template_with_comb_text_field_right_aligned,
    expect_pdf,
):
    obj = PdfWrapper(sample_template_with_comb_text_field_right_aligned).fill(
        {
            "FirstName": "John",
            "MiddleName": "Joe",
            "LastName": "XXXXXX",
            "Awesomeness": True,
            "Gender": 0,
        }
    )

    expect_pdf(obj.read())
