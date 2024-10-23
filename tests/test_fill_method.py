# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_fill_with_varied_int_values(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "fill_method", "sample_filled_varied_ints.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(
            {
                "test": 100,
                "test_2": -250,
                "test_3": 0,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_with_boolean_and_int_values(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "fill_method", "sample_filled_boolean_and_ints.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(
            {
                "test": 42,
                "test_2": True,
                "test_3": False,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_with_empty_string_and_int(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "fill_method", "sample_filled_with_empty_string_and_int.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(
            {
                "test": 42,
                "test_2": "",
                "test_3": 33,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_with_large_and_small_ints(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "fill_method", "sample_filled_large_and_small_ints.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(
            {
                "test": 999999999999,
                "test_2": -999999999999,
                "test_3": 1,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_with_varied_float_values(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "fill_method", "sample_filled_varied_float_values.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(
            {
                "test": 1.5,
                "test_2": 13.8,
                "test_3": 543,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_with_negative_and_positive_floats_and_int(
    template_stream, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples,
        "fill_method",
        "sample_filled_negative_and_positive_floats_and_int.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(
            {
                "test": -1.5,
                "test_2": -6.9,
                "test_3": 22,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
