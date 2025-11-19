# -*- coding: utf-8 -*-

import os

from PyPDFForm import BlankPage, PdfWrapper


def test_blank_page(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_blank_page.pdf")

    blank_pdf = PdfWrapper(BlankPage())

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = blank_pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(blank_pdf.read()) == len(expected)
        request.config.results["skip_regenerate"] = len(blank_pdf.read()) == len(
            expected
        )


def test_blank_page_custom_dimensions(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_blank_page_custom_dimensions.pdf"
    )

    blank_pdf = PdfWrapper(BlankPage(width=595.35, height=841.995))  # A4 size

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = blank_pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(blank_pdf.read()) == len(expected)
        request.config.results["skip_regenerate"] = len(blank_pdf.read()) == len(
            expected
        )


def test_blank_page_multiply(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_blank_page_multiply.pdf")

    blank_pdf = PdfWrapper(BlankPage() * 3)  # 3 pages of letter size

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = blank_pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(blank_pdf.read()) == len(expected)
        request.config.results["skip_regenerate"] = len(blank_pdf.read()) == len(
            expected
        )


def test_extract_pages(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_extract_pages.pdf")

    first_page = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).pages[0]
    first_page.fill(
        {
            "test": "test_1",
            "check": True,
        },
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = first_page.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(first_page.read()) == len(expected)
        assert first_page.read() == expected


def test_merge(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_merge.pdf")

    pdf_one = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
    pdf_two = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    merged = pdf_one + pdf_two

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = merged.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(merged.read()) == len(expected)
        assert merged.read() == expected


def test_reorg_pages(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_reorg_pages.pdf")

    pdf_one = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
    pdf_two = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    merged = pdf_two.pages[0] + pdf_one + pdf_two.pages[1:]

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = merged.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(merged.read()) == len(expected)
        assert merged.read() == expected


def test_change_version(static_pdfs):
    new_version = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf")
    ).change_version("2.0")

    assert new_version.version == "2.0"
