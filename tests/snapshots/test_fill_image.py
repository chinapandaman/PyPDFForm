# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_fill_signature_overlap(pdf_samples, image_samples, expect_pdf):
    obj = PdfWrapper(
        os.path.join(
            pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
        )
    ).fill({"signature": os.path.join(image_samples, "sample_signature.png")})

    expect_pdf(obj.read())


def test_fill_small_icon(pdf_samples, image_samples, expect_pdf):
    obj = PdfWrapper(
        os.path.join(
            pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
        )
    )
    obj.fill({"signature": os.path.join(image_samples, "small_icon.png")})

    expect_pdf(obj.read())


def test_fill_small_icon_not_preserve_aspect_ratio(
    pdf_samples, image_samples, expect_pdf
):
    obj = PdfWrapper(
        os.path.join(
            pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
        )
    )
    obj.widgets["signature"].preserve_aspect_ratio = False
    obj.fill({"signature": os.path.join(image_samples, "small_icon.png")})

    expect_pdf(obj.read())


def test_fill_vertical_image(pdf_samples, image_samples, expect_pdf):
    obj = PdfWrapper(
        os.path.join(
            pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
        )
    )
    obj.fill({"signature": os.path.join(image_samples, "vertical_image.jpg")})

    expect_pdf(obj.read())


def test_fill_vertical_image_not_preserve_aspect_ratio(
    pdf_samples, image_samples, expect_pdf
):
    obj = PdfWrapper(
        os.path.join(
            pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
        )
    )
    obj.widgets["signature"].preserve_aspect_ratio = False
    obj.fill({"signature": os.path.join(image_samples, "vertical_image.jpg")})

    expect_pdf(obj.read())
