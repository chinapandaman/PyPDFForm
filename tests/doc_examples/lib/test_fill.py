# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_fill_text_check(static_pdfs, expect_pdf):
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
        readonly=False,  # optional, set to True to make the filled PDF form read-only
    )

    expect_pdf(filled.read())


def test_fill_radio(static_pdfs, expect_pdf):
    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_radio_button.pdf"),
    ).fill(
        {
            "radio_1": 0,
            "radio_2": 1,
            "radio_3": 2,
        },
        readonly=False,  # optional, set to True to make the filled PDF form read-only
    )

    expect_pdf(filled.read())


def test_fill_dropdown(static_pdfs, expect_pdf):
    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
    ).fill(
        {"dropdown_1": 1},
        readonly=False,  # optional, set to True to make the filled PDF form read-only
    )

    expect_pdf(filled.read())


def test_fill_dropdown_via_str(static_pdfs, expected_pdfs, expect_pdf):
    expected_path = os.path.join(
        expected_pdfs, "doc_examples", "lib", "test_fill", "test_fill_dropdown.pdf"
    )

    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
    ).fill(
        {"dropdown_1": "bar"},
        readonly=False,  # optional, set to True to make the filled PDF form read-only
    )

    expect_pdf(filled.read(), same_as=expected_path)


def test_fill_sig(static_pdfs, image_samples, expect_pdf):
    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_signature.pdf"),
    ).fill(
        {"signature": os.path.join(image_samples, "sample_signature.png")},
        readonly=False,  # optional, set to True to make the filled PDF form read-only
    )

    expect_pdf(filled.read())

    with open(os.path.join(image_samples, "sample_signature.png"), "rb+") as sig:
        filled2 = PdfWrapper(
            os.path.join(static_pdfs, "sample_template_with_signature.pdf"),
        ).fill(
            {"signature": sig},
            readonly=False,  # optional, set to True to make the filled PDF form read-only
        )

    assert filled2.read() == filled.read()

    with open(os.path.join(image_samples, "sample_signature.png"), "rb+") as sig:
        filled3 = PdfWrapper(
            os.path.join(static_pdfs, "sample_template_with_signature.pdf"),
        ).fill(
            {"signature": sig.read()},
            readonly=False,  # optional, set to True to make the filled PDF form read-only
        )

    assert filled3.read() == filled.read()


def test_fill_sig_ratio(static_pdfs, image_samples, expect_pdf):
    pdf = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_signature.pdf"),
    )
    pdf.widgets["signature"].preserve_aspect_ratio = False
    pdf.fill(
        {"signature": os.path.join(image_samples, "sample_signature.png")},
        readonly=False,  # optional, set to True to make the filled PDF form read-only
    )

    expect_pdf(pdf.read())


def test_fill_image(static_pdfs, image_samples, expect_pdf):
    filled = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_image_field.pdf"),
    ).fill(
        {"image_1": os.path.join(image_samples, "sample_image.jpg")},
        readonly=False,  # optional, set to True to make the filled PDF form read-only
    )

    expect_pdf(filled.read())

    with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as img:
        filled2 = PdfWrapper(
            os.path.join(static_pdfs, "sample_template_with_image_field.pdf"),
        ).fill(
            {"image_1": img},
            readonly=False,  # optional, set to True to make the filled PDF form read-only
        )

    assert filled2.read() == filled.read()

    with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as img:
        filled3 = PdfWrapper(
            os.path.join(static_pdfs, "sample_template_with_image_field.pdf"),
        ).fill(
            {"image_1": img.read()},
            readonly=False,  # optional, set to True to make the filled PDF form read-only
        )

    assert filled3.read() == filled.read()


def test_fill_image_ratio(static_pdfs, image_samples, expect_pdf):
    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template_with_image_field.pdf"))
    pdf.widgets["image_1"].preserve_aspect_ratio = True
    pdf.fill(
        {"image_1": os.path.join(image_samples, "sample_image.jpg")},
    )

    expect_pdf(pdf.read())
