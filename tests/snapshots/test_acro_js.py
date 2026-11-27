# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_file_path_scripts(template_stream, pdf_samples, js_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "js", "test_file_path_scripts.pdf")
    pdf = PdfWrapper(template_stream)
    pdf.widgets["test"].on_mouse_pressed_javascript = os.path.join(
        js_samples, "test_file_path_scripts.js"
    )

    expect_pdf(pdf.read(), expected_path)


def test_file_obj_scripts(template_stream, pdf_samples, js_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "js", "test_file_obj_scripts.pdf")
    with open(os.path.join(js_samples, "test_file_obj_scripts.js")) as script:
        pdf = PdfWrapper(template_stream)
        pdf.widgets["test"].on_mouse_pressed_javascript = script

        expect_pdf(pdf.read(), expected_path)


def test_text_field_scripts(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "js", "test_text_field_scripts.pdf")
    pdf = PdfWrapper(template_stream)
    pdf.widgets[
        "test"
    ].on_hovered_over_javascript = 'this.getField("test").value = "hoverover";'
    pdf.widgets[
        "test"
    ].on_hovered_off_javascript = 'this.getField("test").value = "hoveroff";'
    pdf.widgets[
        "test"
    ].on_mouse_pressed_javascript = 'this.getField("test").value = "pressed";'
    pdf.widgets[
        "test"
    ].on_mouse_released_javascript = 'this.getField("test").value = "released";'

    pdf.widgets[
        "test_2"
    ].on_focused_javascript = 'this.getField("test_2").value = "focused";'
    pdf.widgets[
        "test_2"
    ].on_blurred_javascript = 'this.getField("test_2").value = "defocused";'

    expect_pdf(pdf.read(), expected_path)


def test_checkbox_scripts(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "js", "test_checkbox_scripts.pdf")
    pdf = PdfWrapper(template_stream)
    pdf.widgets[
        "check"
    ].on_hovered_over_javascript = 'this.getField("test").value = "hoverover";'
    pdf.widgets[
        "check"
    ].on_hovered_off_javascript = 'this.getField("test").value = "hoveroff";'
    pdf.widgets[
        "check"
    ].on_mouse_pressed_javascript = 'this.getField("test").value = "pressed";'
    pdf.widgets[
        "check"
    ].on_mouse_released_javascript = 'this.getField("test").value = "released";'

    pdf.widgets[
        "check_2"
    ].on_focused_javascript = 'this.getField("test_2").value = "focused";'
    pdf.widgets[
        "check_2"
    ].on_blurred_javascript = 'this.getField("test_2").value = "defocused";'

    expect_pdf(pdf.read(), expected_path)


def test_radio_scripts(template_with_radiobutton_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "js", "test_radio_scripts.pdf")
    pdf = PdfWrapper(template_with_radiobutton_stream)
    pdf.widgets[
        "radio_1"
    ].on_hovered_over_javascript = 'this.getField("test").value = "hoverover";'
    pdf.widgets[
        "radio_1"
    ].on_hovered_off_javascript = 'this.getField("test").value = "hoveroff";'
    pdf.widgets[
        "radio_1"
    ].on_mouse_pressed_javascript = 'this.getField("test").value = "pressed";'
    pdf.widgets[
        "radio_1"
    ].on_mouse_released_javascript = 'this.getField("test").value = "released";'

    pdf.widgets[
        "radio_2"
    ].on_focused_javascript = 'this.getField("test_2").value = "focused";'
    pdf.widgets[
        "radio_2"
    ].on_blurred_javascript = 'this.getField("test_2").value = "defocused";'

    expect_pdf(pdf.read(), expected_path)


def test_dropdown_scripts(sample_template_with_dropdown, pdf_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "js", "test_dropdown_scripts.pdf")
    pdf = PdfWrapper(sample_template_with_dropdown)
    pdf.widgets[
        "dropdown_1"
    ].on_hovered_over_javascript = 'this.getField("test_1").value = "hoverover";'
    pdf.widgets[
        "dropdown_1"
    ].on_hovered_off_javascript = 'this.getField("test_1").value = "hoveroff";'
    pdf.widgets[
        "dropdown_1"
    ].on_mouse_pressed_javascript = 'this.getField("test_1").value = "pressed";'
    pdf.widgets[
        "dropdown_1"
    ].on_mouse_released_javascript = 'this.getField("test_1").value = "released";'

    pdf.widgets[
        "dropdown_1"
    ].on_focused_javascript = 'this.getField("test_2").value = "focused";'
    pdf.widgets[
        "dropdown_1"
    ].on_blurred_javascript = 'this.getField("test_2").value = "defocused";'

    expect_pdf(pdf.read(), expected_path)


def test_image_scripts(sample_template_with_image_field, pdf_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "js", "test_image_scripts.pdf")
    pdf = PdfWrapper(sample_template_with_image_field)
    pdf.widgets[
        "image_1"
    ].on_hovered_over_javascript = 'this.getField("test").value = "hoverover";'
    pdf.widgets[
        "image_1"
    ].on_hovered_off_javascript = 'this.getField("test").value = "hoveroff";'
    pdf.widgets[
        "image_1"
    ].on_mouse_pressed_javascript = 'this.getField("test").value = "pressed";'
    pdf.widgets[
        "image_1"
    ].on_mouse_released_javascript = 'this.getField("test").value = "released";'

    pdf.widgets[
        "image_1"
    ].on_focused_javascript = 'this.getField("test_2").value = "focused";'
    pdf.widgets[
        "image_1"
    ].on_blurred_javascript = 'this.getField("test_2").value = "defocused";'

    expect_pdf(pdf.read(), expected_path)


def test_on_open_script(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "js", "test_on_open_script.pdf")
    pdf = PdfWrapper(template_stream, need_appearances=True)
    pdf.on_open_javascript = 'this.getField("test").value = "opened";'

    expect_pdf(pdf.read(), expected_path)


def test_on_open_script_title_coexist(template_stream, pdf_samples, expect_pdf):
    expected_path = os.path.join(
        pdf_samples, "js", "test_on_open_script_title_coexist.pdf"
    )
    pdf = PdfWrapper(template_stream, title="My PDF")
    pdf.on_open_javascript = 'this.getField("test").value = "opened";'

    expect_pdf(pdf.read(), expected_path)

    pdf2 = PdfWrapper(template_stream)
    pdf2.on_open_javascript = 'this.getField("test").value = "opened";'
    pdf2.title = "My PDF"

    expect_pdf(pdf2.read(), same_as=expected_path)
