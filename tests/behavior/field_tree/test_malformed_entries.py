# -*- coding: utf-8 -*-

from io import BytesIO

import pytest
from pikepdf import Name, Object, Pdf, String
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    NullObject,
    NumberObject,
    TextStringObject,
)

from PyPDFForm import PdfWrapper
from PyPDFForm.lib.field_tree import get_field_keys
from tests.support.builders import get_field, group_fields, save, with_null_named_widget
from tests.support.checks import find_widget, get_field_and_widgets


def test_change_null_text_field_entries(template_stream, assert_widgets_match_output):
    writer = PdfWriter(BytesIO(template_stream))
    for annot in writer.pages[0]["/Annots"]:
        annot = annot.get_object()
        if annot.get("/T") == "test":
            annot[NameObject("/Q")] = NullObject()
            annot[NameObject("/MaxLen")] = NullObject()
    with BytesIO() as f:
        writer.write(f)
        stream = f.getvalue()

    # null entries are absent, so the field has no alignment or maximum length
    obj = PdfWrapper(stream)
    assert obj.widgets["test"].alignment is None
    assert obj.widgets["test"].max_length is None
    obj.widgets["test"].alignment = 1
    obj.widgets["test"].max_length = 4
    widget = find_widget(obj.read(), "test")

    assert widget["/Q"] == 1
    assert widget["/MaxLen"] == 4
    assert_widgets_match_output(obj)


@pytest.mark.parametrize(
    ("name", "entry", "parent", "own", "expected"),
    [
        ("alignment", "/Q", Name("/invalid"), None, None),
        ("alignment", "/Q", 5, None, None),
        # the first value found decides, as viewers use it, and isn't skipped
        # for a valid one above it
        ("alignment", "/Q", 2, Name("/invalid"), None),
        ("alignment", "/Q", 2, -1, None),
        ("alignment", "/Q", 2, String("1"), None),
        ("alignment", "/Q", 1, Object.parse(b"2.0"), 2),
        ("max_length", "/MaxLen", Name("/invalid"), None, None),
        ("max_length", "/MaxLen", -1, None, None),
        ("max_length", "/MaxLen", 4, 0, None),
        ("max_length", "/MaxLen", 4, Object.parse(b"2.5"), None),
        ("max_length", "/MaxLen", 4, Object.parse(b"3.0"), 3),
    ],
)
def test_read_malformed_text_field_entry(
    template_stream, name, entry, parent, own, expected, assert_widgets_match_output
):
    # "test" and "test_2" share a parent with the entry, and "test" may have
    # its own
    stream = group_fields(template_stream, ("test", "test_2"), entry, parent)
    if own is not None:
        with Pdf.open(BytesIO(stream)) as pdf:
            group = get_field(pdf, "group")
            next(kid for kid in group.Kids if str(kid.T) == "test")[entry] = own
            stream = save(pdf)

    # a malformed value means that the field has none
    obj = PdfWrapper(stream)
    assert getattr(obj.widgets["test"], name) == expected
    assert obj.schema["properties"]["test"].get("maxLength") == (
        expected if name == "max_length" else None
    )
    shared = getattr(obj.widgets["test_2"], name)

    setattr(obj.widgets["test"], name, 1)
    reopened = PdfWrapper(obj.read())
    assert getattr(reopened.widgets["test"], name) == 1
    assert getattr(reopened.widgets["test_2"], name) == shared
    assert_widgets_match_output(obj)


@pytest.mark.parametrize(
    ("name", "entry"), [("alignment", "/Q"), ("max_length", "/MaxLen")]
)
def test_clear_text_field_entry_over_malformed_parent(
    template_stream, name, entry, assert_widgets_match_output
):
    stream = group_fields(template_stream, ("test", "test_2"), entry, Name("/invalid"))
    obj = PdfWrapper(stream)
    obj.widgets["test"].alignment = 2
    obj.read()

    # the shared parent's value is malformed, so it doesn't give the field one
    setattr(obj.widgets["test"], name, None)
    result = obj.read()

    assert find_widget(result, "test")["/Parent"].get_object()[entry] == "/invalid"
    assert getattr(PdfWrapper(result).widgets["test"], name) is None
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_widget_with_null_name_belongs_to_its_field(
    template_stream, use_full_widget_name, assert_widgets_match_output
):
    obj = PdfWrapper(
        with_null_named_widget(template_stream),
        use_full_widget_name=use_full_widget_name,
    )
    # the widget with a null name has no key of its own, and reads its field
    assert not any("NullObject" in key for key in obj.widgets)
    assert obj.widgets["test"].value == "value"
    assert obj.widgets["test"].tooltip == "tooltip"

    obj.widgets["test"].alignment = 2
    obj.widgets["test"].max_length = 9
    obj.widgets["test"].tooltip = None
    obj.fill({"test": "new"})
    field, widgets = get_field_and_widgets(obj.read(), "test")

    # changes go to the field, not to a widget
    assert (field["/Q"], field["/MaxLen"], field["/V"]) == (2, 9, "new")
    assert "/TU" not in field
    for widget in widgets:
        assert not {"/Q", "/MaxLen", "/V", "/TU"} & set(widget)
    assert_widgets_match_output(obj)


def test_rename_field_with_null_named_widget(template_stream):
    obj = PdfWrapper(with_null_named_widget(template_stream))
    # renamed through the second widget, whose name is null
    obj.update_widget_key("test", "renamed", 1)
    obj.commit_widget_key_updates()
    _, widgets = get_field_and_widgets(obj.read(), "renamed")

    # the field is renamed, and the widget isn't given a name of its own
    assert isinstance(widgets[1]["/T"], NullObject)
    assert "test" not in obj.widgets
    assert obj.widgets["renamed"].value == "value"
    assert PdfWrapper(obj.read()).widgets["renamed"].value == "value"


def test_remove_field_whose_kid_has_null_name(template_stream):
    # "group", which no page shows, lists a kid with a null /T that doesn't
    # name it as its /Parent; the kid is a widget of "group", not a field
    writer = PdfWriter(BytesIO(template_stream))
    kid = DictionaryObject({NameObject("/T"): NullObject()})
    group = DictionaryObject(
        {
            NameObject("/T"): TextStringObject("group"),
            NameObject("/Kids"): ArrayObject([kid]),
        }
    )
    writer.root_object["/AcroForm"]["/Fields"].append(group)
    with BytesIO() as f:
        writer.write(f)
        stream = f.getvalue()

    assert "group" in get_field_keys(stream, False)
    assert None not in get_field_keys(stream, False)
    output = PdfWrapper(stream).remove_fields(["group"]).read()
    fields = PdfReader(BytesIO(output)).root_object["/AcroForm"]["/Fields"]
    assert "group" not in [str(each.get_object().get("/T")) for each in fields]


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize("parent", [None, NullObject(), NumberObject(5)])
@pytest.mark.parametrize("name", [None, NullObject()], ids=["absent", "null"])
def test_text_field_without_name(template_stream, name, parent, use_full_widget_name):
    # the merged field and widget "test" loses its name, or has a null one, and
    # may have a /Parent that isn't a dictionary, which is absent too
    writer = PdfWriter(BytesIO(template_stream))
    for annot in writer.pages[0]["/Annots"]:
        annot = annot.get_object()
        if annot.get("/T") == "test":
            if name is None:
                del annot["/T"]
            else:
                annot[NameObject("/T")] = name
            if parent is not None:
                annot[NameObject("/Parent")] = parent
            annot[NameObject("/MaxLen")] = NumberObject(4)
    with BytesIO() as f:
        writer.write(f)
        stream = f.getvalue()

    # it opens as a field of its own, without a name
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    key = "" if use_full_widget_name else None
    assert obj.widgets[key].max_length == 4
    assert obj.sample_data[key] == ""

    obj.fill({key: "ab"})
    reopened = PdfWrapper(obj.read(), use_full_widget_name=use_full_widget_name)
    assert reopened.widgets[key].value == "ab"
