# -*- coding: utf-8 -*-
# ruff: noqa: SIM115

import os

from PyPDFForm import PdfWrapper


def test_js_adapting(static_pdfs, pdf_samples, js_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_js_adapting.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.widgets["test"].on_hovered_over_javascript = os.path.join(
        js_samples, "doc_examples", "test_js_adapting.js"
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected

    form2 = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form2.widgets["test"].on_hovered_over_javascript = open(
        os.path.join(js_samples, "doc_examples", "test_js_adapting.js")
    )

    assert form2.read() == form.read()

    form3 = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form3.widgets["test"].on_hovered_over_javascript = open(
        os.path.join(js_samples, "doc_examples", "test_js_adapting.js")
    ).read()

    assert form3.read() == form.read()


def test_on_hover(static_pdfs, pdf_samples, js_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_on_hover.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.widgets["test"].on_hovered_over_javascript = os.path.join(
        js_samples, "doc_examples", "test_on_hover.js"
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_off_hover(static_pdfs, pdf_samples, js_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_off_hover.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.widgets["test"].on_hovered_off_javascript = os.path.join(
        js_samples, "doc_examples", "test_off_hover.js"
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_mouse_pressed(static_pdfs, pdf_samples, js_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_mouse_pressed.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.widgets["test"].on_mouse_pressed_javascript = os.path.join(
        js_samples, "doc_examples", "test_mouse_pressed.js"
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_mouse_released(static_pdfs, pdf_samples, js_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_mouse_released.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.widgets["test"].on_mouse_released_javascript = os.path.join(
        js_samples, "doc_examples", "test_mouse_released.js"
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected
