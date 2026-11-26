# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_fill_sejda_complex(
    sejda_template_complex, sejda_complex_data, pdf_samples, expect_pdf
):
    expected_path = os.path.join(
        pdf_samples, "paragraph", "test_fill_sejda_complex.pdf"
    )
    obj = PdfWrapper(sejda_template_complex).fill(sejda_complex_data)

    expect_pdf(obj.read(), expected_path)


def test_fill_sejda_complex_readonly(
    sejda_template_complex, sejda_complex_data, pdf_samples, expect_pdf
):
    expected_path = os.path.join(
        pdf_samples, "paragraph", "test_fill_sejda_complex_readonly.pdf"
    )
    obj = PdfWrapper(sejda_template_complex).fill(
        sejda_complex_data,
        readonly=True,
    )

    expect_pdf(obj.read(), expected_path)


def test_paragraph_complex(sample_template_paragraph_complex, pdf_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "paragraph", "test_paragraph_complex.pdf")
    obj = PdfWrapper(sample_template_paragraph_complex).fill(
        {
            "paragraph_font_auto_left": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "paragraph_font_auto_right": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "paragraph_font_auto_center": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "paragraph_font_ten_left": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "paragraph_font_ten_right": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            "paragraph_font_ten_center": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
        }
    )

    expect_pdf(obj.read(), expected_path)


def test_paragraph_max_length(
    sample_template_with_paragraph_max_length, pdf_samples, expect_pdf
):
    expected_path = os.path.join(
        pdf_samples, "paragraph", "test_paragraph_max_length.pdf"
    )
    obj = PdfWrapper(sample_template_with_paragraph_max_length).fill(
        {
            "paragraph": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
        }
    )

    expect_pdf(obj.read(), expected_path)
