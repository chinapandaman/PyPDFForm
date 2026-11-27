# -*- coding: utf-8 -*-
# ruff: noqa: SIM115

import os

from PyPDFForm import PdfWrapper


def test_js_adapting(static_pdfs, js_samples, expect_pdf):
    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.widgets["test"].on_hovered_over_javascript = os.path.join(
        js_samples, "doc_examples", "test_js_adapting.js"
    )

    expect_pdf(form.read())

    form2 = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form2.widgets["test"].on_hovered_over_javascript = open(
        os.path.join(js_samples, "doc_examples", "test_js_adapting.js")
    )  # in practice, use a context manager

    assert form2.read() == form.read()

    form3 = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form3.widgets["test"].on_hovered_over_javascript = open(
        os.path.join(js_samples, "doc_examples", "test_js_adapting.js")
    ).read()  # in practice, use a context manager

    assert form3.read() == form.read()


def test_on_hover(static_pdfs, js_samples, expect_pdf):
    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.widgets["test"].on_hovered_over_javascript = os.path.join(
        js_samples, "doc_examples", "test_on_hover.js"
    )

    expect_pdf(form.read())


def test_off_hover(static_pdfs, js_samples, expect_pdf):
    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.widgets["test"].on_hovered_off_javascript = os.path.join(
        js_samples, "doc_examples", "test_off_hover.js"
    )

    expect_pdf(form.read())


def test_mouse_pressed(static_pdfs, js_samples, expect_pdf):
    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.widgets["test"].on_mouse_pressed_javascript = os.path.join(
        js_samples, "doc_examples", "test_mouse_pressed.js"
    )

    expect_pdf(form.read())


def test_mouse_released(static_pdfs, js_samples, expect_pdf):
    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.widgets["test"].on_mouse_released_javascript = os.path.join(
        js_samples, "doc_examples", "test_mouse_released.js"
    )

    expect_pdf(form.read())


def test_on_focused(static_pdfs, js_samples, expect_pdf):
    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.widgets["test"].on_focused_javascript = os.path.join(
        js_samples, "doc_examples", "test_on_focused.js"
    )

    expect_pdf(form.read())


def test_off_focused(static_pdfs, js_samples, expect_pdf):
    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.widgets["test"].on_blurred_javascript = os.path.join(
        js_samples, "doc_examples", "test_off_focused.js"
    )

    expect_pdf(form.read())


def test_on_open(static_pdfs, js_samples, expect_pdf):
    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.on_open_javascript = os.path.join(
        js_samples, "doc_examples", "test_on_open.js"
    )
    assert form.on_open_javascript == 'this.getField("test").value = "opened";\n'

    expect_pdf(form.read())
