# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pikepdf
import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    IndirectObject,
    NameObject,
    NullObject,
    TextStringObject,
)

from PyPDFForm import BlankPage, Fields, PdfWrapper
from PyPDFForm.lib.constants import TU, Parent, V
from PyPDFForm.lib.middleware.radio import Radio
from PyPDFForm.lib.patterns import get_widget_key
from PyPDFForm.lib.template import get_widgets_by_page
from tests.support.builders import (
    change_widgets,
    drop_page,
    drop_page_from_copies,
    hide_target_form,
    javascript,
    set_flags,
)
from tests.support.checks import find_widget


def test_encrypted_edit_pdf_form(issue_pdf_directory, expect_pdf):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "437.pdf"))
    obj = obj.fill(obj.sample_data)
    expect_pdf(obj.read())


def test_fill_image(issue_pdf_directory, image_samples, expect_pdf):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "560.pdf"))
    obj = obj.fill({"ImageSign": os.path.join(image_samples, "sample_image.jpg")})
    expect_pdf(obj.read())


def test_ppf_627_schema(issue_pdf_directory):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-627.pdf"))

    assert obj.schema["properties"]["S1 GF 7"]["maximum"] == 3


def test_ppf_627_fill_1(issue_pdf_directory, expect_pdf):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-627.pdf")).fill(
        {"S1 GF 7": 1}
    )

    expect_pdf(obj.read())


def test_ppf_2100_refill_inline_widget(issue_pdf_directory, assert_catalog_fields):
    # saved by PyPDFForm before PPF-2100 after checking check_2 and removing
    # test_2: check_2's widget is inline in /Annots, with a copy in /Fields
    path = os.path.join(issue_pdf_directory, "PPF-2100.pdf")
    reader = PdfReader(path)
    assert not isinstance(reader.pages[1]["/Annots"][0], IndirectObject)
    assert (reader.get_fields() or {})["check_2"]["/V"] == "/Yes"
    names = ["test", "check", "check_2", "test_3", "check_3"]

    stream = PdfWrapper(path).fill({"check_2": False}).read()

    assert_catalog_fields(stream, names)
    assert (PdfReader(BytesIO(stream)).get_fields() or {})["check_2"]["/V"] == "/Off"
    # an unchecked checkbox reads False or None
    assert not PdfWrapper(stream).data["check_2"]

    # saving it again keeps one entry per field
    assert_catalog_fields(PdfWrapper(stream).read(), names)


def test_ppf_2100_inline_parent(issue_pdf_directory, assert_catalog_fields):
    # saved by PyPDFForm before PPF-2100: the widget's /Parent is inline with
    # /V old, and /Fields has a copy of it
    path = os.path.join(issue_pdf_directory, "PPF-2100-inline-parent.pdf")
    widget = PdfReader(path).pages[0]["/Annots"][0].get_object()
    assert not isinstance(widget.raw_get(Parent), IndirectObject)

    stream = PdfWrapper(path).fill({"name": "new"}).read()

    assert_catalog_fields(stream, ["name"])
    reader = PdfReader(BytesIO(stream))
    assert (reader.get_fields() or {})["name"]["/V"] == "new"
    widget = reader.pages[0]["/Annots"][0].get_object()
    assert widget.raw_get(Parent) == reader.root_object["/AcroForm"]["/Fields"][0]


@pytest.mark.parametrize(
    ("inline_actions", "expected_format"),
    [
        (None, "format_copy();"),
        (
            lambda: DictionaryObject(
                {NameObject("/F"): javascript("format_inline();")}
            ),
            "format_inline();",
        ),
        (NullObject, "format_copy();"),
        (
            lambda: DictionaryObject(
                {NameObject("/C"): NullObject(), NameObject("/TU"): NullObject()}
            ),
            "format_copy();",
        ),
    ],
    ids=["copy", "both", "null", "null_entries"],
)
def test_ppf_2100_inline_parent_keeps_catalog_entries(
    issue_pdf_directory, inline_actions, expected_format
):
    # the copy in /Fields has calculation and format actions and a tooltip,
    # and is in the calculation order; the inline parent has no /AA, or a
    # null /TU with its own format action, a null /AA, or null triggers, and
    # null entries count as absent
    writer = PdfWriter(
        clone_from=os.path.join(issue_pdf_directory, "PPF-2100-inline-parent.pdf")
    )
    acroform = writer.root_object["/AcroForm"]
    copy = acroform["/Fields"][0]
    copy.get_object()[NameObject("/AA")] = DictionaryObject(
        {
            NameObject("/C"): javascript("calculate();"),
            NameObject("/F"): javascript("format_copy();"),
        }
    )
    copy.get_object()[NameObject(TU)] = TextStringObject("tooltip")
    acroform[NameObject("/CO")] = ArrayObject([copy])
    inline = writer.pages[0]["/Annots"][0].get_object()[Parent]
    if inline_actions is not None:
        inline[NameObject("/AA")] = inline_actions()
        inline[NameObject(TU)] = NullObject()
    with BytesIO() as f:
        writer.write(f)
        stream = f.getvalue()

    reader = PdfReader(BytesIO(PdfWrapper(stream).read()))

    acroform = reader.root_object["/AcroForm"]
    field = acroform["/Fields"][0]
    assert reader.pages[0]["/Annots"][0].get_object().raw_get(Parent) == field
    assert acroform["/CO"][0] == field
    actions = field.get_object()["/AA"]
    assert actions["/C"]["/JS"] == "calculate();"
    # the inline parent's action wins for a trigger both have
    assert actions["/F"]["/JS"] == expected_format
    assert field.get_object()[TU] == "tooltip"
    assert field.get_object()[V] == "old"


def test_ppf_2100_stale_page_reference(
    issue_pdf_directory, assert_catalog_fields, assert_page_ownership
):
    # page 1's widget has a /P naming page 2; the page listing it decides which
    # copy it reuses, and the copy keeps its /P
    writer = PdfWriter(
        clone_from=os.path.join(issue_pdf_directory, "PPF-2100-hide-target.pdf")
    )
    page_1, page_2 = writer.pages
    page_1["/Annots"][0].get_object()[NameObject("/P")] = page_2.indirect_reference
    with BytesIO() as f:
        writer.write(f)
        stream = PdfWrapper(f.getvalue()).read()

    assert_catalog_fields(stream, ["shared"])
    assert_page_ownership(stream)
    reader = PdfReader(BytesIO(stream))
    target = reader.root_object["/OpenAction"].raw_get("/T")
    assert list(reader.pages[1]["/Annots"]) == [target]


def test_ppf_2100_inline_fields_keep_version(issue_pdf_directory):
    with open(
        os.path.join(issue_pdf_directory, "PPF-2100-inline-parent.pdf"), "rb"
    ) as f:
        stream = f.read().replace(b"%PDF-1.3", b"%PDF-1.7", 1)

    assert PdfWrapper(stream).version == "1.7"


@pytest.mark.parametrize(
    "edit", [None, set_flags, drop_page], ids=["saved", "edited", "widgets"]
)
def test_ppf_2100_hide_target(issue_pdf_directory, assert_catalog_fields, edit):
    # each page widget reuses the copy whose /P is its page, even if the widget
    # was changed or lost its own /P
    stream = PdfWrapper(hide_target_form(issue_pdf_directory, edit)).read()

    assert_catalog_fields(stream, ["shared"])
    reader = PdfReader(BytesIO(stream))
    target = reader.root_object["/OpenAction"].raw_get("/T")
    assert list(reader.pages[1]["/Annots"]) == [target]
    assert target.get_object().raw_get("/P") == reader.pages[1].indirect_reference
    if edit is set_flags:
        assert target.get_object()["/F"] == 4


def test_ppf_2100_ambiguous_inline_widgets(issue_pdf_directory):
    # without /P on the page widgets and their copies, each page widget matches
    # both copies, so neither copy is reused and the Hide action keeps its
    # target
    stream = PdfWrapper(
        hide_target_form(issue_pdf_directory, drop_page_from_copies)
    ).read()

    reader = PdfReader(BytesIO(stream))
    target = reader.root_object["/OpenAction"].raw_get("/T")
    widgets = [page["/Annots"][0] for page in reader.pages]
    assert target not in widgets
    assert all(widget in widget.get_object()["/Parent"]["/Kids"] for widget in widgets)


def test_ppf_2100_fill_inline_signature(
    issue_pdf_directory, image_samples, assert_catalog_fields
):
    # saved by PyPDFForm before PPF-2100 after removing a text field from page
    # 2: the signature widget is inline, and /Fields has a copy of it
    path = os.path.join(issue_pdf_directory, "PPF-2100-inline-signature.pdf")
    assert not isinstance(PdfReader(path).pages[1]["/Annots"][0], IndirectObject)

    stream = (
        PdfWrapper(path)
        .fill({"signature": os.path.join(image_samples, "sample_image.jpg")})
        .read()
    )

    assert_catalog_fields(stream, ["text_1"])
    assert list(PdfReader(BytesIO(stream)).get_fields() or {}) == ["text_1"]


def test_ppf_2128_remove_hidden_button(issue_pdf_directory):
    # ImageSign runs JavaScript and then hides the LoadImage button by name
    def get_action(stream):
        page = PdfReader(BytesIO(stream)).pages[0]
        return next(
            annot.get_object()["/A"]
            for annot in page["/Annots"]
            if annot.get_object().get("/T") == "ImageSign"
        )

    obj = PdfWrapper(os.path.join(issue_pdf_directory, "560.pdf"))
    script = get_action(obj.read())["/JS"]
    assert get_action(obj.read())["/Next"] == {"/S": "/Hide", "/T": "LoadImage"}

    action = get_action(obj.remove_fields(["LoadImage"]).read())

    assert action["/S"] == "/JavaScript"
    assert action["/JS"] == script
    # the Hide does nothing, and stays so that the chain keeps its shape
    assert action["/Next"] == {"/S": "/Hide", "/T": []}


@pytest.mark.parametrize(
    "options",
    [{}, {"need_appearances": True}, {"generate_appearance_streams": True}],
    ids=["default", "need-appearances", "generate-appearance-streams"],
)
def test_ppf_2153_malformed_appearance_dictionaries(
    template_filled_stream, options, assert_valid_appearances
):
    # test_2's appearance dictionary has no /N, and check_2's appearance state
    # names a state that its appearance doesn't have
    template = change_widgets(
        template_filled_stream,
        {
            "test_2": lambda annot: setattr(
                annot, "AP", pikepdf.Dictionary(D=annot.AP.N)
            ),
            "check_2": lambda annot: setattr(annot, "AS", pikepdf.Name("/Missing")),
        },
    )
    with pytest.raises(AssertionError):
        assert_valid_appearances(template)

    for data in (None, {"test": "new"}, {"test_2": "new"}):
        form = PdfWrapper(template, **options)
        output = (form.fill(data) if data else form).read()

        assert_valid_appearances(output)
        # viewers draw test_2 from its value, unless the generator draws it
        assert ("/AP" in find_widget(output, "test_2")) == (
            "generate_appearance_streams" in options
        )
        # the state that check_2's value names, which PyPDFForm reads
        assert find_widget(output, "check_2")["/AS"] == "/Yes"
        assert PdfWrapper(output).data["check_2"] is True


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


def test_use_full_widget_name_1(issue_pdf_directory, expect_pdf):
    obj = PdfWrapper(
        os.path.join(issue_pdf_directory, "PPF-939.pdf"), use_full_widget_name=True
    ).fill(
        {
            "topmostSubform[0].Page1[0].c1_3[1]": False,
            "topmostSubform[0].Page1[0].FilingStatus_ReadOrder[0].c1_3[1]": True,
        }
    )

    expect_pdf(obj.read())


def test_use_full_widget_name_2(issue_pdf_directory, expect_pdf):
    obj = PdfWrapper(
        os.path.join(issue_pdf_directory, "PPF-939.pdf"), use_full_widget_name=True
    ).fill(
        {
            "topmostSubform[0].Page1[0].c1_3[1]": True,
            "topmostSubform[0].Page1[0].FilingStatus_ReadOrder[0].c1_3[1]": False,
        }
    )

    expect_pdf(obj.read())


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

    result = PdfReader(BytesIO(obj.read()))

    for i, page in enumerate(result.pages):
        page_data = data[i]
        for widget in page.annotations or []:
            key = get_widget_key(widget, use_full_widget_name=False)
            for k, v in page_data.items():
                if key.startswith(k):
                    assert widget[Parent][V] == v


def test_xfa_to_regular_form(issue_pdf_directory, expect_pdf):
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

    # widgets on each page share a short name but keep their own values,
    # since the key isn't filled
    barcodes = [
        annot.get_object()[V]
        for page in PdfReader(BytesIO(obj.read())).pages
        for annot in page["/Annots"]
        if annot.get_object().get("/T") == "PDF417BarCode1[0]"
    ]
    assert barcodes == [f"I-140|06/07/24|{page}" for page in range(1, 9)]
    expect_pdf(obj.read())


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


def test_get_dropdown_choices(issue_pdf_directory, expect_pdf):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-1213.pdf")).fill(
        {
            "Dropdown8": 1,
            "Dropdown9": 2,
            "Dropdown10": 3,
            "Dropdown11": 4,
        }
    )

    expect_pdf(obj.read())


def test_sejda_multiline(issue_pdf_directory, expect_pdf):
    obj = PdfWrapper(os.path.join(issue_pdf_directory, "PPF-1349.pdf")).fill(
        {
            "Nombre corp": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas rhoncus est turpis, vitae hendrerit magna vestibulum in. Nulla maximus consectetur varius. Ut lectus nulla, malesuada at felis dictum, tristique lacinia lacus. Phasellus vehicula dui a orci aliquam, at tempus orci consequat. Maecenas sagittis auctor magna, a scelerisque urna ullamcorper at. Nam pellentesque faucibus condimentum. In hac habitasse platea dictumst.",
            "Nombre rep": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas rhoncus est turpis, vitae hendrerit magna vestibulum in. Nulla maximus consectetur varius. Ut lectus nulla, malesuada at felis dictum, tristique lacinia lacus. Phasellus vehicula dui a orci aliquam, at tempus orci consequat. Maecenas sagittis auctor magna, a scelerisque urna ullamcorper at. Nam pellentesque faucibus condimentum. In hac habitasse platea dictumst.",
            "Nombre bnf": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas rhoncus est turpis, vitae hendrerit magna vestibulum in. Nulla maximus consectetur varius. Ut lectus nulla, malesuada at felis dictum, tristique lacinia lacus. Phasellus vehicula dui a orci aliquam, at tempus orci consequat. Maecenas sagittis auctor magna, a scelerisque urna ullamcorper at. Nam pellentesque faucibus condimentum. In hac habitasse platea dictumst.",
            "Poblacion CERREM corp": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas rhoncus est turpis, vitae hendrerit magna vestibulum in. Nulla maximus consectetur varius. Ut lectus nulla, malesuada at felis dictum, tristique lacinia lacus. Phasellus vehicula dui a orci aliquam, at tempus orci consequat. Maecenas sagittis auctor magna, a scelerisque urna ullamcorper at. Nam pellentesque faucibus condimentum. In hac habitasse platea dictumst.",
            "Poblacion CERREM rep": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas rhoncus est turpis, vitae hendrerit magna vestibulum in. Nulla maximus consectetur varius. Ut lectus nulla, malesuada at felis dictum, tristique lacinia lacus. Phasellus vehicula dui a orci aliquam, at tempus orci consequat. Maecenas sagittis auctor magna, a scelerisque urna ullamcorper at. Nam pellentesque faucibus condimentum. In hac habitasse platea dictumst.",
            "Poblacion CERREM bnf": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas rhoncus est turpis, vitae hendrerit magna vestibulum in. Nulla maximus consectetur varius. Ut lectus nulla, malesuada at felis dictum, tristique lacinia lacus. Phasellus vehicula dui a orci aliquam, at tempus orci consequat. Maecenas sagittis auctor magna, a scelerisque urna ullamcorper at. Nam pellentesque faucibus condimentum. In hac habitasse platea dictumst.",
        },
        readonly=True,
    )

    expect_pdf(obj.read())


def test_not_merge_metadata():
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
    wrapper = PdfWrapper(pdf_stream)
    wrapper.bulk_create_fields(
        [Fields.TextField(name="Test", page_number=1, x=100, y=400)]
    )
    new_stream = BytesIO(wrapper.read())
    reader = PdfReader(new_stream)
    metadata = reader.metadata or {}
    assert metadata["/test_key"] == "test_value"
    assert metadata["/other_key"] == "other_value"


def test_dropdown_tutorial(expect_pdf):
    obj = PdfWrapper(BlankPage(width=612, height=792) * 3)
    obj.generate_coordinate_grid(margin=100, color=(0, 0, 1))

    obj.bulk_create_fields(
        [
            Fields.TextField(
                name="text_field_custom_text",
                page_number=1,
                x=100,
                y=700,
                font_size=25,
                font_color=(1, 0, 0),
            ),
            Fields.TextField(
                name="text_field_misc",
                page_number=1,
                x=100,
                y=600,
                alignment=2,
                max_length=5,
            ),
            Fields.TextField(
                name="text_field_paragraph",
                page_number=1,
                x=100,
                y=400,
                width=200,
                height=100,
                multiline=True,
            ),
            Fields.RadioGroup(
                name="radio",
                page_number=1,
                x=[300, 400, 500],
                y=[700, 700, 700],
            ),
            Fields.RadioGroup(
                name="radio_cutomized",
                page_number=1,
                x=[300, 400, 500],
                y=[600, 600, 600],
                size=50,
                shape="square",
                button_style="diamond",
                tick_color=(0, 0, 1),
            ),
            Fields.DropdownField(
                name="dropdown",
                page_number=2,
                x=100,
                y=600,
                options=["dog", "cat", "fish"],
            ),
        ]
    )

    expect_pdf(obj.read())
