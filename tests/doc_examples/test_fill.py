# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_fill_text_check(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_text_check.pdf")

    filled = PdfWrapper(
        template_stream,
        adobe_mode=False,  # optional, set to True for Adobe Acrobat compatibility
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


def test_fill_radio(template_with_radiobutton_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_radio.pdf")

    filled = PdfWrapper(
        template_with_radiobutton_stream,
        adobe_mode=False,  # optional, set to True for Adobe Acrobat compatibility
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


def test_fill_dropdown(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_dropdown.pdf")

    filled = PdfWrapper(
        os.path.join(pdf_samples, "dropdown", "sample_template_with_dropdown.pdf"),
        adobe_mode=False,  # optional, set to True for Adobe Acrobat compatibility
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


def test_fill_dropdown_via_str(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_dropdown.pdf")

    filled = PdfWrapper(
        os.path.join(pdf_samples, "dropdown", "sample_template_with_dropdown.pdf"),
        adobe_mode=False,  # optional, set to True for Adobe Acrobat compatibility
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


def test_fill_sig(pdf_samples, image_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_sig.pdf")

    filled = PdfWrapper(
        os.path.join(pdf_samples, "signature", "sample_template_with_signature.pdf"),
        adobe_mode=False,  # optional, set to True for Adobe Acrobat compatibility
    ).fill(
        {"signature": os.path.join(image_samples, "sample_signature.png")},
        flatten=False,  # optional, set to True to flatten the filled PDF form
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = filled.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        if os.name != "nt":
            assert len(filled.read()) == len(expected)
            assert filled.read() == expected


def test_fill_sig_ratio(pdf_samples, image_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_sig_ratio.pdf")

    pdf = PdfWrapper(
        os.path.join(pdf_samples, "signature", "sample_template_with_signature.pdf"),
        adobe_mode=False,  # optional, set to True for Adobe Acrobat compatibility
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

        if os.name != "nt":
            assert len(pdf.read()) == len(expected)
            assert pdf.read() == expected


def test_fill_image(
    sample_template_with_image_field, pdf_samples, image_samples, request
):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_image.pdf")

    filled = PdfWrapper(
        sample_template_with_image_field,
        adobe_mode=False,  # optional, set to True for Adobe Acrobat compatibility
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


def test_fill_image_ratio(
    sample_template_with_image_field, pdf_samples, image_samples, request
):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_image_ratio.pdf")

    pdf = PdfWrapper(sample_template_with_image_field)
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
