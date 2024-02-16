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
