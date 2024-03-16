# -*- coding: utf-8 -*-

import os

from PyPDFForm import FormWrapper


def test_fill_max_length_text_field_all_chars(
    sample_template_with_max_length_text_field, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "simple", "max_length_text_field_related",
                                 "max_length_text_field_all_chars.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_max_length_text_field).fill(
            {
                "FirstName": "John",
                "MiddleName": "Joe",
                "LastName": "XXXXXXXXXX",
                "Awesomeness": True,
                "Gender": 0,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.stream)
        assert obj.read() == obj.stream

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream == expected
