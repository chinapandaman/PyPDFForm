# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_preview(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "preview", "test_preview.pdf")
    with open(expected_path, "rb+") as f:
        preview = PdfWrapper(template_stream).preview

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = preview

        expected = f.read()

        assert len(preview) == len(expected)
        assert preview == expected


def test_preview_sejda(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "preview", "test_preview_sejda.pdf")
    with open(expected_path, "rb+") as f:
        preview = PdfWrapper(sejda_template).preview

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = preview

        expected = f.read()

        assert len(preview) == len(expected)
        assert preview == expected


def test_preview_paragraph_complex(
    sample_template_paragraph_complex, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "preview", "test_preview_paragraph_complex.pdf"
    )
    with open(expected_path, "rb+") as f:
        preview = PdfWrapper(sample_template_paragraph_complex).preview

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = preview

        expected = f.read()

        if os.name != "nt":
            assert len(preview) == len(expected)
            assert preview == expected


def test_preview_sejda_complex(sejda_template_complex, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "preview", "test_preview_sejda_complex.pdf"
    )
    with open(expected_path, "rb+") as f:
        preview = PdfWrapper(sejda_template_complex).preview

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = preview

        expected = f.read()

        assert len(preview) == len(expected)
        assert preview == expected


def test_preview_comb_text_field(
    sample_template_with_comb_text_field, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "preview", "test_preview_comb_text_field.pdf"
    )
    with open(expected_path, "rb+") as f:
        preview = PdfWrapper(sample_template_with_comb_text_field).preview

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = preview

        expected = f.read()

        assert len(preview) == len(expected)
        assert preview == expected
