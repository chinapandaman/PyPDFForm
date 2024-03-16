# -*- coding: utf-8 -*-

import os

from PyPDFForm import FormWrapper


def test_paragraph_y_coordinate(sample_template_with_paragraph, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "paragraph", "test_paragraph_y_coordinate.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(sample_template_with_paragraph).fill(
            {"paragraph_1": "test paragraph"}
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected
