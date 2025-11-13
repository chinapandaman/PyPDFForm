# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import PdfWrapper


def test_fill_text_check(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_text_check.pdf")

    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf"),
    ).fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
        flatten=False,  # optional, set to True to flatten the filled PDF form
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = filled.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(filled.read()) == len(expected)
        assert filled.read() == expected


def test_fill_radio(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_radio.pdf")

    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_radio_button.pdf"),
    ).fill(
        {
            "radio_1": 0,
            "radio_2": 1,
            "radio_3": 2,
        },
        flatten=False,  # optional, set to True to flatten the filled PDF form
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = filled.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(filled.read()) == len(expected)
        assert filled.read() == expected


def test_fill_dropdown(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_dropdown.pdf")

    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
    ).fill(
        {"dropdown_1": 1},
        flatten=False,  # optional, set to True to flatten the filled PDF form
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = filled.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(filled.read()) == len(expected)
        assert filled.read() == expected


def test_fill_dropdown_via_str(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_dropdown.pdf")

    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
    ).fill(
        {"dropdown_1": "bar"},
        flatten=False,  # optional, set to True to flatten the filled PDF form
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = filled.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(filled.read()) == len(expected)
        assert filled.read() == expected


@pytest.mark.posix_only
def test_fill_sig(static_pdfs, pdf_samples, image_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_sig.pdf")

    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_signature.pdf"),
    ).fill(
        {"signature": os.path.join(image_samples, "sample_signature.png")},
        flatten=False,  # optional, set to True to flatten the filled PDF form
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = filled.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(filled.read()) == len(expected)
        assert filled.read() == expected


@pytest.mark.posix_only
def test_fill_sig_ratio(static_pdfs, pdf_samples, image_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_sig_ratio.pdf")

    pdf = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_signature.pdf"),
    )
    pdf.widgets["signature"].preserve_aspect_ratio = False
    pdf.fill(
        {"signature": os.path.join(image_samples, "sample_signature.png")},
        flatten=False,  # optional, set to True to flatten the filled PDF form
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_fill_image(static_pdfs, pdf_samples, image_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_image.pdf")

    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_image_field.pdf"),
    ).fill(
        {"image_1": os.path.join(image_samples, "sample_image.jpg")},
        flatten=False,  # optional, set to True to flatten the filled PDF form
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = filled.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(filled.read()) == len(expected)
        assert filled.read() == expected


def test_fill_image_ratio(static_pdfs, pdf_samples, image_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_image_ratio.pdf")

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template_with_image_field.pdf"))
    pdf.widgets["image_1"].preserve_aspect_ratio = True
    pdf.fill(
        {"image_1": os.path.join(image_samples, "sample_image.jpg")},
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected
