# -*- coding: utf-8 -*-

import os

from PyPDFForm import FormWrapper


def test_pdf_form_with_central_aligned_text_fields(issue_pdf_directory, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "scenario", "issues", "PPF-285-expected.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(os.path.join(issue_pdf_directory, "PPF-285.pdf")).fill(
            {
                "name": "Hans Mustermann",
                "fulladdress": "Musterstr. 12, 82903 Musterdorf, Musterland",
                "advisorname": "Karl Test",
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected
