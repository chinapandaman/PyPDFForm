# -*- coding: utf-8 -*-

import os

from PyPDFForm import Annotations, PdfWrapper


def test_text_annotations(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_text_annotations.pdf")

    annotations = [
        Annotations.TextAnnotation(
            page_number=1,
            x=310,
            y=663,
            contents="this is an annotation",  # optional
            title="First Annotation",  # optional
        ),
        Annotations.TextAnnotation(
            page_number=2,
            x=310,
            y=672,
            contents="this is another annotation",  # optional
            title="Second Annotation",  # optional
            icon=Annotations.TextAnnotation.comment_icon,  # optional
        ),
    ]

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).annotate(
        annotations
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_uri_link_annotations(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_uri_link_annotations.pdf")

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).annotate(
        [
            Annotations.LinkAnnotation(
                page_number=1,
                x=70,
                y=705,
                width=95,
                height=20,
                uri="https://www.google.com/",
            )
        ]
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_page_link_annotations(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_page_link_annotations.pdf")

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).annotate(
        [
            Annotations.LinkAnnotation(
                page_number=1,
                x=70,
                y=705,
                width=95,
                height=20,
                page=2,
            )
        ]
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_highlight_annotations(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_highlight_annotations.pdf")

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).annotate(
        [
            Annotations.HighlightAnnotation(
                page_number=1, x=70, y=705, width=95, height=20
            )
        ]
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_underline_annotations(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_underline_annotations.pdf")

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).annotate(
        [
            Annotations.UnderlineAnnotation(
                page_number=1, x=70, y=705, width=95, height=20
            )
        ]
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_squiggly_annotations(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_squiggly_annotations.pdf")

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).annotate(
        [
            Annotations.SquigglyAnnotation(
                page_number=1, x=70, y=705, width=95, height=20
            )
        ]
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_strikeout_annotations(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_strikeout_annotations.pdf")

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).annotate(
        [
            Annotations.StrikeOutAnnotation(
                page_number=1, x=70, y=705, width=95, height=20
            )
        ]
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_rubber_stamp_annotations(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_rubber_stamp_annotations.pdf"
    )

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).annotate(
        [
            Annotations.RubberStampAnnotation(
                page_number=1,
                x=70,
                y=720,
                width=95,
                height=20,
                name=Annotations.RubberStampAnnotation.approved,  # optional
            )
        ]
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected
