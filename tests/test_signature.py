# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_fill_signature(pdf_samples, image_samples, request):
    expected_path = os.path.join(pdf_samples, "signature", "test_fill_signature.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(pdf_samples, "signature", "sample_template_with_signature.pdf")
        ).fill({"signature": os.path.join(image_samples, "sample_signature.png")})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        if os.name != "nt":
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected


def test_signature_schema(pdf_samples):
    obj = PdfWrapper(
        os.path.join(pdf_samples, "signature", "sample_template_with_signature.pdf")
    )

    assert obj.widgets["signature"].schema_definition == {"type": "string"}


def test_signature_sample_value(pdf_samples):
    obj = PdfWrapper(
        os.path.join(pdf_samples, "signature", "sample_template_with_signature.pdf")
    )

    assert obj.widgets["signature"].sample_value == os.path.expanduser(
        "~/Downloads/sample_image.jpg"
    )


def test_fill_signature_overlap(pdf_samples, image_samples, request):
    expected_path = os.path.join(
        pdf_samples, "signature", "test_fill_signature_overlap.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(
                pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
            )
        ).fill({"signature": os.path.join(image_samples, "sample_signature.png")})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        if os.name != "nt":
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected


def test_fill_signature_overlap_not_preserve_aspect_ratio(
    pdf_samples, image_samples, request
):
    expected_path = os.path.join(
        pdf_samples,
        "signature",
        "test_fill_signature_overlap_not_preserve_aspect_ratio.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(
                pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
            )
        )
        obj.widgets["signature"].preserve_aspect_ratio = False
        obj.fill({"signature": os.path.join(image_samples, "sample_signature.png")})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        if os.name != "nt":
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected


def test_fill_small_icon(pdf_samples, image_samples, request):
    expected_path = os.path.join(pdf_samples, "signature", "test_fill_small_icon.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(
                pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
            )
        )
        obj.fill({"signature": os.path.join(image_samples, "small_icon.png")})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        if os.name != "nt":
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected


def test_fill_small_icon_not_preserve_aspect_ratio(pdf_samples, image_samples, request):
    expected_path = os.path.join(
        pdf_samples, "signature", "test_fill_small_icon_not_preserve_aspect_ratio.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(
                pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
            )
        )
        obj.widgets["signature"].preserve_aspect_ratio = False
        obj.fill({"signature": os.path.join(image_samples, "small_icon.png")})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        if os.name != "nt":
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected


def test_fill_vertical_image(pdf_samples, image_samples, request):
    expected_path = os.path.join(
        pdf_samples, "signature", "test_fill_vertical_image.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(
                pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
            )
        )
        obj.fill({"signature": os.path.join(image_samples, "vertical_image.jpg")})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        if os.name != "nt":
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected


def test_fill_vertical_image_not_preserve_aspect_ratio(
    pdf_samples, image_samples, request
):
    expected_path = os.path.join(
        pdf_samples,
        "signature",
        "test_fill_vertical_image_not_preserve_aspect_ratio.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(
                pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
            )
        )
        obj.widgets["signature"].preserve_aspect_ratio = False
        obj.fill({"signature": os.path.join(image_samples, "vertical_image.jpg")})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        if os.name != "nt":
            assert len(obj.read()) == len(expected)
            assert obj.read() == expected
