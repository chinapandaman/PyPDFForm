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
