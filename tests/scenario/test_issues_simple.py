# -*- coding: utf-8 -*-
# pylint: disable=line-too-long

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


def test_pdf_form_with_paragraph_fields_new_line_symbol_text(issue_pdf_directory, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "scenario", "issues", "PPF-415-expected.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(os.path.join(issue_pdf_directory, "PPF-415.pdf")).fill(
            {"Address": "Mr John Smith\n132, My Street\nKingston, New York 12401"}
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_pdf_form_with_paragraph_fields_new_line_symbol_text_overflow(issue_pdf_directory, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "simple", "scenario", "issues", "PPF-415-2-expected.pdf")
    with open(expected_path, "rb+") as f:
        obj = FormWrapper(os.path.join(issue_pdf_directory, "PPF-415-2.pdf")).fill(
            {
                "multiline-text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Malesuada proin libero nunc consequat interdum varius sit amet mattis. Nec tincidunt praesent semper feugiat nibh sed.\nSed libero enim sed faucibus turpis. Cursus in hac habitasse platea dictumst quisque sagittis. Placerat in egestas erat imperdiet sed euismod. Id aliquet risus feugiat in ante metus dictum at. Proin fermentum leo vel orci porta non pulvinar. Consequat semper viverra nam libero justo.\nPellentesque massa placerat duis ultricies lacus sed. Amet est placerat in egestas erat imperdiet sed euismod nisi. Id cursus metus aliquam eleifend mi. Massa massa ultricies mi quis. Volutpat consequat mauris nunc congue nisi vitae suscipit tellus. Ut tellus elementum sagittis vitae.\n\nEtiam sit amet nisl purus in mollis nunc. Vel turpis nunc eget lorem dolor sed. Ultrices dui sapien eget mi proin sed libero enim. Condimentum id venenatis a condimentum vitae sapien pellentesque habitant. Libero volutpat sed cras ornare arcu. Commodo quis imperdiet massa tincidunt nunc pulvinar sapien et ligula. Nisi est sit amet facilisis magna etiam. In iaculis nunc sed augue.\nSapien pellentesque habitant morbi tristique.\nCondimentum mattis pellentesque id nibh tortor id aliquet. Porttitor massa id neque aliquam vestibulum. Feugiat in fermentum posuere urna nec tincidunt praesent semper. Malesuada fames ac turpis egestas integer. Aenean vel elit scelerisque mauris pellentesque. Vel turpis nunc eget lorem dolor sed viverra. Nec feugiat nisl pretium fusce id velit ut tortor." # noqa
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected
