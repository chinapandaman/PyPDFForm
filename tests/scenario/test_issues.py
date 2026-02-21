# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from pypdf import PdfReader, PdfWriter

from PyPDFForm import BlankPage, Fields, PdfWrapper
from PyPDFForm.constants import TU, Parent, V
from PyPDFForm.middleware.radio import Radio
from PyPDFForm.patterns import get_widget_key
from PyPDFForm.template import get_widgets_by_page
from PyPDFForm.utils import stream_to_io


@pytest.mark.posix_only
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
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


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


def test_ppf_627_schema(issue_pdf_directory):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-627.pdf"))

    assert obj.schema["properties"]["S1 GF 7"]["maximum"] == 3


def test_ppf_627_fill_1(issue_pdf_directory, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-627.pdf")).fill(
        {"S1 GF 7": 1}
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-627-expected-1.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_get_desc_in_schema(issue_pdf_directory):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "757.pdf"))

    assert (
        obj.schema["properties"]["P1_checkbox4[0]"]["description"]
        == "Part 1. Information About You. Your Full Name. 4. Has your name legally changed since the issuance of your Permanent Resident Card? Select Yes. (Proceed to Item Numbers 5. A. through 5. C.)."
    )
    assert (
        obj.schema["properties"]["P1_checkbox4[1]"]["description"]
        == "Part 1. Information About You. Your Full Name. 4. Has your name legally changed since the issuance of your Permanent Resident Card? Select No (Proceed to Item Numbers 6. A. through 6. I.)."
    )
    assert (
        obj.schema["properties"]["P1_checkbox4[2]"]["description"]
        == "Part 1. Information About You. Your Full Name. 4. Has your name legally changed since the issuance of your Permanent Resident Card? Select Not Applicable - I never received my previous card. (Proceed to Item Numbers 6. A. through 6. I.)."
    )


def test_get_desc_in_schema_radio(issue_pdf_directory):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-620.pdf"))

    keys_to_check = []
    for key, value in obj.widgets.items():
        if isinstance(value, Radio) and value.tooltip is not None:
            keys_to_check.append(key)

    for widgets in get_widgets_by_page(obj.read()).values():
        for widget in widgets:
            key = get_widget_key(widget, False)

            if key in keys_to_check:
                assert (
                    widget[Parent][TU] == obj.schema["properties"][key]["description"]
                )


def test_use_full_widget_name_1(issue_pdf_directory, request):
    obj = PdfWrapper(
        os.path.join(issue_pdf_directory, "PPF-939.pdf"), use_full_widget_name=True
    ).fill(
        {
            "topmostSubform[0].Page1[0].c1_3[1]": False,
            "topmostSubform[0].Page1[0].FilingStatus_ReadOrder[0].c1_3[1]": True,
        }
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-939_expected_1.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_use_full_widget_name_2(issue_pdf_directory, request):
    obj = PdfWrapper(
        os.path.join(issue_pdf_directory, "PPF-939.pdf"), use_full_widget_name=True
    ).fill(
        {
            "topmostSubform[0].Page1[0].c1_3[1]": True,
            "topmostSubform[0].Page1[0].FilingStatus_ReadOrder[0].c1_3[1]": False,
        }
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-939_expected_2.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_use_full_widget_name_both(issue_pdf_directory):
    obj = PdfWrapper(
        os.path.join(issue_pdf_directory, "PPF-939.pdf"), use_full_widget_name=True
    ).fill(
        {
            "topmostSubform[0].Page1[0].c1_3[1]": True,
            "topmostSubform[0].Page1[0].FilingStatus_ReadOrder[0].c1_3[1]": True,
        }
    )

    assert (
        obj.read()
        == PdfWrapper(os.path.join(issue_pdf_directory, "PPF-939.pdf"))
        .fill(
            {
                "c1_3[1]": True,
            }
        )
        .read()
    )


def test_merge_sejda_pdf_forms(issue_pdf_directory):
    data = [
        {"name": "John", "dob": "1990-01-01", "note": "test1"},
        {"name": "James", "dob": "1992-06-15", "note": "test2"},
        {"name": "Dan", "dob": "1988-12-30", "note": "test3"},
    ]

    obj = PdfWrapper(need_appearances=True)

    for i in range(3):
        obj += PdfWrapper(
            os.path.join(issue_pdf_directory, "PPF-884.pdf"), need_appearances=True
        ).fill(data[i])

    result = PdfReader(stream_to_io(obj.read()))

    for i, page in enumerate(result.pages):
        page_data = data[i]
        for widget in page.annotations or []:
            key = get_widget_key(widget, use_full_widget_name=False)
            for k, v in page_data.items():
                if key.startswith(k):
                    assert widget[Parent][V] == v


def test_xfa_to_regular_form(issue_pdf_directory, request):
    obj = PdfWrapper(
        os.path.join(issue_pdf_directory, "1087.pdf"), need_appearances=True
    ).fill(
        {
            "G28CheckBox[0]": True,
            "Pt1Line1a_FamilyName[0]": "Mylastname",
            "Pt1Line1b_GivenName[0]": "Myfirstname",
            "Line2_CompanyName[0]": "The company LLC",
        }
    )

    expected_path = os.path.join(issue_pdf_directory, "1087_expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_full_widget_name(issue_pdf_directory):
    obj = PdfWrapper(
        os.path.join(issue_pdf_directory, "PPF-1159.pdf"), use_full_widget_name=True
    )

    assert "Ancestry.Page 1" in obj.widgets


def test_extract_multiline_property(issue_pdf_directory):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-1162.pdf"))

    for k, v in obj.widgets.items():
        if "AdditionalInfo" in k:
            assert v.multiline


def test_get_dropdown_choices(issue_pdf_directory, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-1213.pdf")).fill(
        {
            "Dropdown8": 1,
            "Dropdown9": 2,
            "Dropdown10": 3,
            "Dropdown11": 4,
        }
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-1213_expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_sejda_multiline(issue_pdf_directory, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-1349.pdf")).fill(
        {
            "Nombre corp": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas rhoncus est turpis, vitae hendrerit magna vestibulum in. Nulla maximus consectetur varius. Ut lectus nulla, malesuada at felis dictum, tristique lacinia lacus. Phasellus vehicula dui a orci aliquam, at tempus orci consequat. Maecenas sagittis auctor magna, a scelerisque urna ullamcorper at. Nam pellentesque faucibus condimentum. In hac habitasse platea dictumst.",
            "Nombre rep": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas rhoncus est turpis, vitae hendrerit magna vestibulum in. Nulla maximus consectetur varius. Ut lectus nulla, malesuada at felis dictum, tristique lacinia lacus. Phasellus vehicula dui a orci aliquam, at tempus orci consequat. Maecenas sagittis auctor magna, a scelerisque urna ullamcorper at. Nam pellentesque faucibus condimentum. In hac habitasse platea dictumst.",
            "Nombre bnf": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas rhoncus est turpis, vitae hendrerit magna vestibulum in. Nulla maximus consectetur varius. Ut lectus nulla, malesuada at felis dictum, tristique lacinia lacus. Phasellus vehicula dui a orci aliquam, at tempus orci consequat. Maecenas sagittis auctor magna, a scelerisque urna ullamcorper at. Nam pellentesque faucibus condimentum. In hac habitasse platea dictumst.",
            "Poblacion CERREM corp": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas rhoncus est turpis, vitae hendrerit magna vestibulum in. Nulla maximus consectetur varius. Ut lectus nulla, malesuada at felis dictum, tristique lacinia lacus. Phasellus vehicula dui a orci aliquam, at tempus orci consequat. Maecenas sagittis auctor magna, a scelerisque urna ullamcorper at. Nam pellentesque faucibus condimentum. In hac habitasse platea dictumst.",
            "Poblacion CERREM rep": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas rhoncus est turpis, vitae hendrerit magna vestibulum in. Nulla maximus consectetur varius. Ut lectus nulla, malesuada at felis dictum, tristique lacinia lacus. Phasellus vehicula dui a orci aliquam, at tempus orci consequat. Maecenas sagittis auctor magna, a scelerisque urna ullamcorper at. Nam pellentesque faucibus condimentum. In hac habitasse platea dictumst.",
            "Poblacion CERREM bnf": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas rhoncus est turpis, vitae hendrerit magna vestibulum in. Nulla maximus consectetur varius. Ut lectus nulla, malesuada at felis dictum, tristique lacinia lacus. Phasellus vehicula dui a orci aliquam, at tempus orci consequat. Maecenas sagittis auctor magna, a scelerisque urna ullamcorper at. Nam pellentesque faucibus condimentum. In hac habitasse platea dictumst.",
        },
        flatten=True,
    )

    expected_path = os.path.join(issue_pdf_directory, "PPF-1349_expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_preserve_metadata():
    pdf_stream = BytesIO(PdfWrapper(BlankPage()).read())
    writer = PdfWriter(pdf_stream)
    writer.add_metadata(
        {
            "/test_key": "test_value",
            "/other_key": "other_value",
        }
    )
    writer.write(pdf_stream)
    pdf_stream.seek(0)
    wrapper = PdfWrapper(pdf_stream, preserve_metadata=True)
    wrapper.create_field(Fields.TextField(name="Test", page_number=1, x=100, y=400))
    new_stream = BytesIO(wrapper.read())
    reader = PdfReader(new_stream)
    metadata = reader.metadata or {}
    assert metadata["/test_key"] == "test_value"
    assert metadata["/other_key"] == "other_value"

    assert PdfWrapper(preserve_metadata=True)


def test_change_field_resolutions(issue_pdf_directory, request):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-1552.pdf"))
    obj.widgets["topmostSubform[0].Page3[0].Liczbadni3a[0]"].x -= 5
    obj.widgets["topmostSubform[0].Page3[0].Liczbadni3a[0]"].width += 25
    obj.widgets["topmostSubform[0].Page3[0].Liczbadni3a[0]"].y -= 1
    obj.widgets["topmostSubform[0].Page3[0].Liczbadni3a[0]"].height += 1
    obj.fill({"topmostSubform[0].Page3[0].Liczbadni3a[0]": "23"})

    expected_path = os.path.join(issue_pdf_directory, "PPF-1552_expected.pdf")
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(expected_path, "rb+") as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
