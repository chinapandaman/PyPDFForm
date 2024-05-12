# -*- coding: utf-8 -*-
# pylint: disable=line-too-long

import os

from PyPDFForm import PdfWrapper


def test_pdf_form_with_pages_without_widgets(issue_pdf_directory, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-246.pdf")).fill(
        {"QCredit": "5000.63"}
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-246-expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_pdf_form_with_central_aligned_text_fields(issue_pdf_directory, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-285.pdf")).fill(
        {
            "name": "Hans Mustermann",
            "fulladdress": "Musterstr. 12, 82903 Musterdorf, Musterland",
            "advisorname": "Karl Test",
        }
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-285-expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_pdf_form_with_central_aligned_text_fields_void(issue_pdf_directory):
    assert PdfWrapper(os.path.join(issue_pdf_directory, "PPF-285.pdf")).fill({}).read()


def test_pdf_form_with_paragraph_fields_new_line_symbol_text(
    issue_pdf_directory, request
):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-415.pdf")).fill(
        {"Address": "Mr John Smith\n132, My Street\nKingston, New York 12401"}
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-415-expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        if os.name != "nt":
            assert abs(len(obj.read()) - len(expected)) <= 1


def test_pdf_form_with_paragraph_fields_new_line_symbol_text_overflow(
    issue_pdf_directory, request
):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-415-2.pdf")).fill(
        {
            "multiline-text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Malesuada proin libero nunc consequat interdum varius sit amet mattis. Nec tincidunt praesent semper feugiat nibh sed.\nSed libero enim sed faucibus turpis. Cursus in hac habitasse platea dictumst quisque sagittis. Placerat in egestas erat imperdiet sed euismod. Id aliquet risus feugiat in ante metus dictum at. Proin fermentum leo vel orci porta non pulvinar. Consequat semper viverra nam libero justo.\nPellentesque massa placerat duis ultricies lacus sed. Amet est placerat in egestas erat imperdiet sed euismod nisi. Id cursus metus aliquam eleifend mi. Massa massa ultricies mi quis. Volutpat consequat mauris nunc congue nisi vitae suscipit tellus. Ut tellus elementum sagittis vitae.\n\nEtiam sit amet nisl purus in mollis nunc. Vel turpis nunc eget lorem dolor sed. Ultrices dui sapien eget mi proin sed libero enim. Condimentum id venenatis a condimentum vitae sapien pellentesque habitant. Libero volutpat sed cras ornare arcu. Commodo quis imperdiet massa tincidunt nunc pulvinar sapien et ligula. Nisi est sit amet facilisis magna etiam. In iaculis nunc sed augue.\nSapien pellentesque habitant morbi tristique.\nCondimentum mattis pellentesque id nibh tortor id aliquet. Porttitor massa id neque aliquam vestibulum. Feugiat in fermentum posuere urna nec tincidunt praesent semper. Malesuada fames ac turpis egestas integer. Aenean vel elit scelerisque mauris pellentesque. Vel turpis nunc eget lorem dolor sed viverra. Nec feugiat nisl pretium fusce id velit ut tortor."  # noqa
        }
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-415-2-expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_521(issue_pdf_directory, request):
    expected_path = os.path.join(issue_pdf_directory, "521-expected.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(os.path.join(issue_pdf_directory, "521.pdf")).fill(
            {
                "Text1": "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?",  # noqa
                "Text2": "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. NEMO ENIM IPSAM VOLUPTATEM QUIA VOLUPTAS SIT ASPERNATUR AUT ODIT AUT FUGIT, SED QUIA CONSEQUUNTUR MAGNI DOLORES EOS QUI RATIONE VOLUPTATEM SEQUI NESCIUNT. NEQUE PORRO QUISQUAM EST, QUI DOLOREM IPSUM QUIA DOLOR SIT AMET, CONSECTETUR, ADIPISCI VELIT, SED QUIA NON NUMQUAM EIUS MODI TEMPORA INCIDUNT UT LABORE ET DOLORE MAGNAM ALIQUAM QUAERAT VOLUPTATEM. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?",  # noqa
                "Text3": "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?",  # noqa
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.stream == expected


def test_pdf_form_with_paragraph_fields_new_line_symbol_short_text(
    issue_pdf_directory, request
):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-415.pdf")).fill(
        {"Address": "J Smith\n132 A St\nNYC, NY 12401"}
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-415-3-expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        if os.name != "nt":
            assert abs(len(obj.read()) - len(expected)) <= 1


def test_encrypted_edit_pdf_form(issue_pdf_directory, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "437.pdf"))
    obj = obj.fill(obj.sample_data)
    expected_path = os.path.join(issue_pdf_directory, "437_expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_image(issue_pdf_directory, image_samples, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "560.pdf"))
    obj = obj.fill({"ImageSign": os.path.join(image_samples, "sample_image.jpg")})
    expected_path = os.path.join(issue_pdf_directory, "560_expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_reduce_paragraph_overflow_text_font_size(issue_pdf_directory, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-620.pdf")).fill(
        {
            "301 What Happened": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris congue, lorem sit amet venenatis lacinia, quam tortor pharetra ante, id facilisis neque velit ac tellus. Nam tincidunt felis quis eros malesuada, ac congue elit consequat. Ut eget porttitor augue. Integer ullamcorper lectus et est scelerisque, ac posuere mi tempor. Nunc vulputate vehicula bibendum. Aliquam erat volutpat. Morbi tortor."  # noqa
        }
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-620-expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_PPF_627_schema(issue_pdf_directory):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-627.pdf"))

    assert obj.schema["properties"]["S1 GF 7"]["maximum"] == 3


def test_PPF_627_fill_0(issue_pdf_directory, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-627.pdf")).fill(
        {
            "S1 GF 7": 0
        }
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-627-expected-0.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_PPF_627_fill_1(issue_pdf_directory, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-627.pdf")).fill(
        {
            "S1 GF 7": 1
        }
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-627-expected-1.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_PPF_627_fill_2(issue_pdf_directory, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-627.pdf")).fill(
        {
            "S1 GF 7": 2
        }
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-627-expected-2.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_PPF_627_fill_3(issue_pdf_directory, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-627.pdf")).fill(
        {
            "S1 GF 7": 3
        }
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-627-expected-3.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
