# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from pikepdf import Array, Name, Pdf, String
from pypdf import PdfWriter
from pypdf.generic import (
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
)

from PyPDFForm import Fields, PdfWrapper
from PyPDFForm.lib.field_tree import get_field_keys
from tests.support.builders import (
    get_field,
    group_fields,
    save,
    with_field_cycle,
    with_named_parent_cycle,
    with_radio_group_in_parent_cycle,
)


@pytest.mark.parametrize(
    ("shape", "key", "short_key"),
    [
        # "a" and "b" are each other's parent
        ("named", "b.a.test", "test"),
        # the widget has no name, so the key is its field's
        ("unnamed", "b.a", "a"),
        ("listed", "b.a", "a"),
        ("root", "b.a", "a"),
        # the parent of "a" is the field
        ("field", "a.test", "test"),
    ],
)
def test_full_widget_name_with_parent_cycle(
    template_stream,
    shape,
    key,
    short_key,
    assert_round_trip,
    assert_widgets_match_output,
):
    stream = with_named_parent_cycle(template_stream, shape)
    others = ["check", "test_2", "check_2", "test_3", "check_3"]
    # the key ends before a field is reached a second time
    obj = PdfWrapper(stream, use_full_widget_name=True)
    assert list(obj.widgets) == [key, *others]
    # the field and its widget have the same key for removal
    assert get_field_keys(stream, True) == {key, *others}
    original = obj.read()
    # the cycle is reached before any flags, so changing one raises
    obj.widgets[key].readonly = True

    with pytest.raises(ValueError, match="the /Parent chain of the field has a cycle"):
        obj.read()

    assert obj.widgets[key].readonly is False
    assert obj.read() == original

    obj.fill({key: "foo"})
    assert_round_trip(obj, {key: "foo"})
    assert_widgets_match_output(obj)

    # removing the field raises and changes nothing, with full names or without
    without_full_names = PdfWrapper(stream)
    without_full_names.fill({short_key: "foo"})
    for each, name in ((obj, key), (without_full_names, short_key)):
        filled = each.read()

        with pytest.raises(
            ValueError, match="the /Parent chain of the field has a cycle"
        ):
            each.remove_fields([name])

        assert each.read() == filled
        assert each.data[name] == "foo"


@pytest.mark.parametrize("shape", ["group", "mutual", "listing", "three"])
@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_remove_fields_in_parent_cycle(
    template_stream, shape, use_full_widget_name, assert_widgets_match_output
):
    obj = PdfWrapper(
        with_field_cycle(template_stream, shape),
        use_full_widget_name=use_full_widget_name,
    )
    obj.fill(
        {
            key: key.split(".")[-1]
            for key in obj.widgets
            if key.split(".")[-1].startswith("test")
        }
    )
    original = obj.read()
    keys = list(obj.widgets)
    test = next(key for key in keys if key.split(".")[-1] == "test")

    # which fields are below "test", and would go with it, isn't defined, so
    # removing it raises and changes nothing, including the other field
    with pytest.raises(ValueError, match="the /Parent chain of the field has a cycle"):
        obj.remove_fields([test, "check"])

    assert obj.read() == original
    assert list(obj.widgets) == keys
    assert_widgets_match_output(obj)

    # a field outside the cycle can be removed
    obj.remove_fields(["check"])
    assert list(obj.widgets) == [key for key in keys if key != "check"]
    assert all(
        obj.data[key] == key.split(".")[-1]
        for key in obj.widgets
        if key.split(".")[-1].startswith("test")
    )


@pytest.mark.parametrize(
    ("first", "second"),
    [("SignatureField", "SignatureField"), ("ImageField", "TextField")],
)
@pytest.mark.parametrize("listing", [False, True], ids=["parents", "listing"])
def test_fill_consumed_widget_in_parent_cycle(
    template_stream, image_samples, first, second, listing
):
    obj = PdfWrapper(template_stream)
    obj.bulk_create_fields(
        [
            getattr(Fields, first)("first", 1, 100, 600, width=100, height=40),
            getattr(Fields, second)("second", 1, 300, 600, width=100, height=40),
        ]
    )
    # the two fields are each other's parent, and may list each other as kids
    with Pdf.open(BytesIO(obj.read())) as pdf:
        first_field, second_field = get_field(pdf, "first"), get_field(pdf, "second")
        first_field.Parent = second_field
        second_field.Parent = first_field
        if listing:
            first_field.Kids = Array([second_field])
            second_field.Kids = Array([first_field])
        stream = save(pdf)

    obj = PdfWrapper(stream, use_full_widget_name=True)
    image = os.path.join(image_samples, "sample_signature.png")
    obj.fill(
        {
            "second.first": image,
            "first.second": image if second == "SignatureField" else "foo",
        }
    )
    widgets = PdfWrapper(obj.read(), use_full_widget_name=True).widgets

    # an image or signature widget is drawn and leaves the page, which doesn't
    # change the other field's key before it is filled
    assert {
        key: widget.value
        for key, widget in widgets.items()
        if key.split(".")[-1] in ("first", "second")
    } == ({} if second == "SignatureField" else {"first.second": "foo"})
    # and the form lists only the other field, which doesn't list it as a kid
    with Pdf.open(BytesIO(obj.read())) as pdf:
        assert [
            str(each.get("/T"))
            for each in pdf.Root.AcroForm.Fields
            if str(each.get("/T")) in ("first", "second")
        ] == ([] if second == "SignatureField" else ["second"])
        assert not [
            kid
            for page in pdf.pages
            for annot in page.get("/Annots", [])
            for kid in annot.get("/Kids", [])
        ]


@pytest.mark.parametrize("shape", ["group", "listing", "three"])
@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_pages_in_parent_cycle(template_stream, shape, use_full_widget_name):
    obj = PdfWrapper(
        with_field_cycle(template_stream, shape),
        use_full_widget_name=use_full_widget_name,
    )
    original = obj.read()
    keys = list(obj.widgets)

    # page 1 keeps only part of a field in the cycle, and the cycle is reached
    # before the field's /Opt is found
    with pytest.raises(
        ValueError,
        match="Cannot copy page 1: the /Parent chain of the field has a cycle",
    ):
        obj.pages  # noqa: B018 # pylint: disable=W0104

    assert obj.read() == original
    assert list(obj.widgets) == keys


@pytest.mark.parametrize(
    ("group", "other", "expected"),
    [
        # /Opt and /V, which names the option that page 1 keeps, are found
        # before the cycle, but /DV isn't
        ({"/V": Name("/0")}, {}, None),
        # /V names the option on page 2, and the cycle is reached before page
        # 1 finds whether a field above "a" has a value
        ({"/V": Name("/1"), "/DV": Name("/1")}, {}, None),
        # every entry is found before the cycle, including on "b", so the
        # pages are split and renumbered
        (
            {"/V": Name("/1"), "/DV": Name.Off},
            {"/V": Name.Off},
            [("x", "/Off", "/Off", None), ("y", "/0", "/0", 0)],
        ),
    ],
    ids=["default", "value", "found"],
)
def test_pages_with_radio_group_in_parent_cycle(
    template_stream, group, other, expected
):
    group = {"/Opt": Array([String("x"), String("y")]), **group}
    obj = PdfWrapper(with_radio_group_in_parent_cycle(template_stream, group, other))
    original = obj.read()

    if expected is None:
        with pytest.raises(
            ValueError,
            match="Cannot copy page 1: the /Parent chain of the field has a cycle",
        ):
            obj.pages  # noqa: B018 # pylint: disable=W0104
        assert obj.read() == original
        return

    pages = obj.pages
    for page, (option, value, state, data) in zip(
        (pages[0], pages[1]), expected, strict=True
    ):
        with Pdf.open(BytesIO(page.read())) as pdf:
            widget = next(annot for annot in pdf.pages[0].Annots if "/Parent" in annot)
            radio = widget.Parent
            # the group keeps only its option on the page
            assert [str(each) for each in radio.Opt] == [option]
            assert len(radio.Kids) == 1
            assert str(radio.V) == value
            assert str(widget.AS) == state
        assert PdfWrapper(page.read()).data["a"] == data
    assert obj.read() == original


@pytest.mark.parametrize("parent", ["missing", "number", "null"])
def test_pages_with_parent_not_a_dictionary(template_stream, parent):
    # "test" (page 1) and "test_2" (page 2) are kids of "group", whose /Parent
    # doesn't resolve to a dictionary, such as an object that doesn't exist
    writer = PdfWriter(
        BytesIO(group_fields(template_stream, ("test", "test_2"), "/Ff", 0))
    )
    group = next(
        each.get_object()
        for each in writer.root_object["/AcroForm"]["/Fields"]
        if each.get_object().get("/T") == "group"
    )
    group[NameObject("/Parent")] = {
        "missing": IndirectObject(9999, 0, writer),
        "number": NumberObject(5),
        "null": NullObject(),
    }[parent]
    with BytesIO() as f:
        writer.write(f)
        stream = f.getvalue()

    # the chain ends there, as ISO 32000-1 treats a missing object as null, so
    # each page keeps its own kid of the group
    pages = PdfWrapper(stream).pages
    for page, name in zip((pages[0], pages[1]), ("test", "test_2"), strict=True):
        with Pdf.open(BytesIO(page.read())) as pdf:
            widget = next(
                annot for annot in pdf.pages[0].Annots if annot.get("/T") == name
            )
            assert [str(kid.T) for kid in widget.Parent.Kids] == [name]
