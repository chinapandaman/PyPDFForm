# -*- coding: utf-8 -*-

import os

from PyPDFForm import BlankPage, PdfArray, PdfWrapper


def test_blank_page(expect_pdf):
    blank_pdf = PdfWrapper(BlankPage())

    expect_pdf(blank_pdf.read(), timestamped=True)

    assert not blank_pdf.widgets
    assert len(blank_pdf.pages) == 1


def test_blank_page_custom_dimensions(expect_pdf):
    blank_pdf = PdfWrapper(BlankPage(width=595.35, height=841.995))  # A4 size

    expect_pdf(blank_pdf.read(), timestamped=True)

    assert not blank_pdf.widgets
    assert len(blank_pdf.pages) == 1


def test_blank_page_multiply(expect_pdf):
    blank_pdf = PdfWrapper(BlankPage() * 3)  # 3 pages of letter size

    expect_pdf(blank_pdf.read(), timestamped=True)

    assert not blank_pdf.widgets
    assert len(blank_pdf.pages) == 3


def test_extract_pages(static_pdfs, expect_pdf):
    first_page = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).pages[0]
    first_page = PdfWrapper(
        first_page.read()
    )  # not in docs, to keep artifact consistent with CLI
    first_page.fill(
        {
            "test": "test_1",
            "check": True,
        },
    )

    expect_pdf(first_page.read())


def test_merge(static_pdfs, pdf_samples, expect_pdf):
    pdf_one = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
    pdf_two = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    merged = pdf_one + pdf_two

    expect_pdf(merged.read())


def test_reorg_pages(static_pdfs, pdf_samples, expect_pdf):
    pdf_one = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
    pdf_two = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    merged = pdf_two.pages[0] + pdf_one + pdf_two.pages[1:]

    expect_pdf(merged.read())


def test_merge_using_pdf_array(static_pdfs, pdf_samples, expected_pdfs, expect_pdf):
    expected_path = os.path.join(
        expected_pdfs, "doc_examples", "lib", "test_utils", "test_merge.pdf"
    )

    pdfs = PdfArray(
        [
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")),
            PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")),
            # can get very large
        ]
    )
    merged = pdfs.merge()

    expect_pdf(merged.read(), same_as=expected_path)


def test_change_version(static_pdfs):
    new_version = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf")
    ).change_version("2.0")

    assert new_version.version == "2.0"
