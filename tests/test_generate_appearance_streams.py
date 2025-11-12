# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


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
