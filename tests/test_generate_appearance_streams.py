# -*- coding: utf-8 -*-
# TODO: why does pikepdf randomize final streams?

import os

import pytest

from PyPDFForm import PdfWrapper
from tests.test_need_appearances import run_sample_template_library_test


def test_fill(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(
        pdf_samples, "generate_appearance_streams", "sample_filled.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream, generate_appearance_streams=True).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        request.config.results["skip_regenerate"] = len(obj.read()) == len(expected)


def test_dropdown_two(sample_template_with_dropdown, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "generate_appearance_streams", "dropdown", "dropdown_two.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            sample_template_with_dropdown, generate_appearance_streams=True
        ).fill(
            {
                "test_1": "test_1",
                "test_2": "test_2",
                "test_3": "test_3",
                "check_1": True,
                "check_2": True,
                "check_3": True,
                "radio_1": 1,
                "dropdown_1": 1,
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        request.config.results["skip_regenerate"] = len(obj.read()) == len(expected)


def test_fill_sejda_complex(
    sejda_template_complex, sejda_complex_data, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples,
        "generate_appearance_streams",
        "paragraph",
        "sample_filled_sejda_complex.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template_complex, generate_appearance_streams=True).fill(
            sejda_complex_data,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        request.config.results["skip_regenerate"] = len(obj.read()) == len(expected)


def test_issue_613(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "generate_appearance_streams", "issues", "613_expected.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(pdf_samples, "scenario", "issues", "613.pdf"),
            generate_appearance_streams=True,
        ).fill(
            {
                "301 Full name": "John Smith",
                "301 Address Street": "1234 road number 6",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        request.config.results["skip_regenerate"] = len(obj.read()) == len(expected)


@pytest.mark.posix_only
def test_sample_template_library(
    pdf_samples, image_samples, sample_font_stream, request
):
    run_sample_template_library_test(
        pdf_samples,
        image_samples,
        sample_font_stream,
        request,
        generate_appearance_streams=True,
    )
