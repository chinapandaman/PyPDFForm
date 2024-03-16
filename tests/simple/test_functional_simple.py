# -*- coding: utf-8 -*-

import os

from PyPDFForm import FormWrapper


def test_fill(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "simple", "sample_filled.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(template_stream).fill(
            data_dict
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.stream)
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected


def test_fill_radiobutton(pdf_samples, template_with_radiobutton_stream, request):
    expected_path = os.path.join(pdf_samples, "simple", "sample_filled_radiobutton.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(template_with_radiobutton_stream).fill(
            {
                "radio_1": 0,
                "radio_2": 1,
                "radio_3": 2,
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_fill_right_aligned(
    sample_template_with_right_aligned_text_field, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "simple", "sample_filled_right_aligned.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_right_aligned_text_field).fill(
            {
                "name": "Hans Mustermann",
                "fulladdress": "Musterstr. 12, 82903 Musterdorf, Musterland",
                "advisorname": "Karl Test",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected
