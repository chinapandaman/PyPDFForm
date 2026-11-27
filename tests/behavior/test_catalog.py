# -*- coding: utf-8 -*-

from io import BytesIO

import pytest
from pikepdf import Dictionary, Name, Pdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    NullObject,
    NumberObject,
    TextStringObject,
)

from PyPDFForm import Annotations, BlankPage, Fields, PdfWrapper, RawElements
from PyPDFForm.lib import egress
from PyPDFForm.lib.constants import AcroForm, T
from PyPDFForm.lib.constants import Fields as FieldsConst
from PyPDFForm.lib.patterns import get_widget_key
from tests.support.builders import save, with_catalog_extras
from tests.support.checks import describe_catalog


def test_sync_acroform_fields(assert_catalog_fields):
    pdf = PdfWrapper(BlankPage() * 2)

    pdf.bulk_create_fields(
        [Fields.TextField("foo", 1, 100, 100), Fields.TextField("bar", 2, 100, 200)]
    )

    assert_catalog_fields(pdf.read(), ["foo", "bar"])
    reader = PdfReader(BytesIO(pdf.read()))

    assert get_widget_key(reader.root_object[AcroForm][FieldsConst][0], False) == "foo"
    assert get_widget_key(reader.root_object[AcroForm][FieldsConst][1], False) == "bar"


def test_sync_acroform_fields_ignores_note_title(assert_catalog_fields):
    form = PdfWrapper(BlankPage()).annotate(
        [
            Annotations.TextAnnotation(
                1, 100, 100, title="signature", contents="keep note"
            )
        ]
    )
    stream = form.read()

    result = egress.sync_acroform_fields(stream)

    assert result == stream
    assert_catalog_fields(result, [])
    reader = PdfReader(BytesIO(result))
    assert reader.pages[0]["/Annots"][0].get_object()["/Contents"] == "keep note"


def test_sync_acroform_fields_inline_widget(assert_catalog_fields):
    # widget annotations should be indirect objects; an inline one is made one,
    # shared by the page and the catalog
    writer = PdfWriter()
    page = writer.add_blank_page(200, 200)
    page[NameObject("/Annots")] = ArrayObject(
        [
            DictionaryObject(
                {
                    NameObject("/Type"): NameObject("/Annot"),
                    NameObject("/Subtype"): NameObject("/Widget"),
                    NameObject("/FT"): NameObject("/Tx"),
                    NameObject(T): TextStringObject("inline"),
                    NameObject("/Rect"): ArrayObject(
                        NumberObject(each) for each in (10, 10, 100, 30)
                    ),
                }
            )
        ]
    )
    with BytesIO() as f:
        writer.write(f)
        stream = f.getvalue()

    result = egress.sync_acroform_fields(stream)

    assert_catalog_fields(result, ["inline"])
    assert list(PdfReader(BytesIO(result)).get_fields()) == ["inline"]
    assert list(PdfWrapper(result).widgets) == ["inline"]


@pytest.mark.parametrize(
    "options",
    [{}, {"need_appearances": True}, {"generate_appearance_streams": True}],
    ids=["default", "need-appearances", "generate-appearance-streams"],
)
def test_sync_acroform_fields_inline_widget_with_indirect_subtype(
    template_stream, options, assert_catalog_fields
):
    # the page lists an inline copy of "test_2" and the catalog the indirect
    # one, and the /Subtype of both is an indirect /Widget
    with Pdf.open(BytesIO(template_stream)) as pdf:
        annots = pdf.pages[1].Annots
        index = next(
            index for index, annot in enumerate(annots) if annot.get("/T") == "test_2"
        )
        annots[index].Subtype = pdf.make_indirect(Name.Widget)
        annots[index] = Dictionary(dict(annots[index].items()))
        stream = save(pdf)

    result = PdfWrapper(stream, **options).read()

    assert_catalog_fields(
        result, ["test", "check", "test_2", "check_2", "test_3", "check_3"]
    )


def test_sync_acroform_fields_inline_parent(assert_catalog_fields):
    # a parent field should be an indirect object; an inline one is made one,
    # shared by its widget and the catalog
    writer = PdfWriter()
    writer.add_blank_page(200, 200)
    widget = writer.add_annotation(
        0,
        {
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Widget"),
            NameObject("/Rect"): ArrayObject(
                NumberObject(each) for each in (10, 10, 100, 30)
            ),
        },
    )
    widget[NameObject("/Parent")] = DictionaryObject(
        {
            NameObject("/FT"): NameObject("/Tx"),
            NameObject(T): TextStringObject("parent"),
            NameObject("/Kids"): ArrayObject([widget.indirect_reference]),
        }
    )
    with BytesIO() as f:
        writer.write(f)
        stream = f.getvalue()

    result = egress.sync_acroform_fields(stream)

    assert_catalog_fields(result, ["parent"])
    with Pdf.open(BytesIO(result)) as pdf:
        parent = pdf.pages[0].Annots[0].Parent
        assert parent.is_indirect
        assert parent.objgen == pdf.Root.AcroForm.Fields[0].objgen


@pytest.mark.parametrize("key", ["/CO", "/Fields"])
def test_null_acroform_entries(template_stream, key):
    # ISO 32000-1 treats a null dictionary value as an absent entry
    writer = PdfWriter(BytesIO(template_stream))
    writer.root_object["/AcroForm"][NameObject(key)] = NullObject()
    with BytesIO() as f:
        writer.write(f)
        stream = f.getvalue()

    result = PdfWrapper(stream).remove_fields(["test"]).read()

    assert sorted(PdfReader(BytesIO(result)).get_fields()) == [
        "check",
        "check_2",
        "check_3",
        "test_2",
        "test_3",
    ]


def test_read_preserves_catalog(template_stream, assert_catalog_fields):
    stream = with_catalog_extras(template_stream)
    expected = describe_catalog(stream)

    assert expected["fields"]["hidden_business_id"] == "12345"
    assert {"submit_button", "group.test_2", "group.test_3"} <= set(expected["fields"])
    assert expected["calculation_order"] == [
        "test",
        "group.test_2",
        "hidden_business_id",
    ]
    assert expected["entries"] == ["/CO", "/DA", "/DR"]
    assert_catalog_fields(stream, list(expected["fields"]))
    result = PdfWrapper(stream).read()
    assert describe_catalog(result) == expected
    assert_catalog_fields(result, list(expected["fields"]))


def test_read_preserves_fields_without_widgets_on_pages(sejda_template):
    # the sejda template lists fields whose widgets are on no page
    def get_names(stream):
        with Pdf.open(BytesIO(stream)) as pdf:
            return sorted(
                str(field.get("/T", "")) for field in pdf.Root.AcroForm.Fields
            )

    names = get_names(sejda_template)

    assert "Buyers Name" in names
    assert get_names(PdfWrapper(sejda_template).read()) == names


@pytest.mark.parametrize(
    ("operation", "changed"),
    [
        (lambda obj: obj.fill({"test": "filled", "check": True}), {"test", "check"}),
        (lambda obj: setattr(obj.widgets["test"], "font_size", 20), set()),
        (
            lambda obj: obj.bulk_create_fields([Fields.TextField("new", 1, 300, 300)]),
            {"new"},
        ),
        (lambda obj: obj.draw([RawElements.RawText("drawn", 1, 300, 300)]), set()),
        (lambda obj: obj.generate_coordinate_grid(), set()),
        (
            lambda obj: obj.update_widget_key(
                "check", "renamed"
            ).commit_widget_key_updates(),
            {"check", "renamed"},
        ),
        (
            lambda obj: obj.annotate(
                [Annotations.TextAnnotation(1, 300, 300, contents="note")]
            ),
            set(),
        ),
    ],
    ids=["fill", "style", "create", "draw", "grid", "rename", "annotate"],
)
def test_unrelated_edits_preserve_catalog(
    template_stream, assert_catalog_fields, operation, changed
):
    stream = with_catalog_extras(template_stream)
    expected = describe_catalog(stream)
    obj = PdfWrapper(stream)

    operation(obj)
    output = obj.read()
    result = describe_catalog(output)

    assert {
        name: value for name, value in result["fields"].items() if name not in changed
    } == {
        name: value for name, value in expected["fields"].items() if name not in changed
    }
    assert result["calculation_order"] == expected["calculation_order"]
    assert result["entries"] == expected["entries"]
    assert_catalog_fields(output, list(result["fields"]))
