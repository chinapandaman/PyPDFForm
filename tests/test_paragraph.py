# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import PdfWrapper


def test_fill_sejda_complex(
    sejda_template_complex, sejda_complex_data, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "paragraph", "test_fill_sejda_complex.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template_complex).fill(sejda_complex_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_sejda_complex_flatten(
    sejda_template_complex, sejda_complex_data, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "paragraph", "test_fill_sejda_complex_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template_complex).fill(
            sejda_complex_data,
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_paragraph_complex(sample_template_paragraph_complex, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "paragraph", "test_paragraph_complex.pdf")
    with open(expected_path, "rb+") as f:
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

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_paragraph_max_length(
    sample_template_with_paragraph_max_length, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "paragraph", "test_paragraph_max_length.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_paragraph_max_length).fill(
            {
                "paragraph": "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
