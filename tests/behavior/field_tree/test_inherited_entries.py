# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from pikepdf import Array, Dictionary, Pdf, String

from PyPDFForm import PdfWrapper
from tests.support.builders import (
    below_unnamed_field,
    get_field,
    group_fields,
    nest_fields,
    pdf_value,
    save,
    set_null_entries,
    set_parent_entry,
    split_widgets,
    with_parent_cycle,
)
from tests.support.checks import find_widget, get_nested_entries

# a text field property, its entry, and values for it: the one chosen by the
# lookup, another one, and the one it is changed to
TEXT_FIELD_ENTRIES = [
    ("alignment", "/Q", 1, 2, 0),
    ("max_length", "/MaxLen", 3, 7, 5),
]


def test_clear_absent_text_field_properties(template_stream):
    obj = PdfWrapper(template_stream)
    entries = ("/Ff", "/TU", "/MaxLen", "/Q")
    annot = find_widget(obj.read(), "test")
    expected = {entry: annot.get(entry) for entry in entries}
    widget = obj.widgets["test"]
    widget.multiline = False
    widget.comb = False
    widget.tooltip = None
    widget.max_length = None
    widget.alignment = None

    # clearing entries the field doesn't have leaves the field unchanged
    annot = find_widget(obj.read(), "test")
    assert {entry: annot.get(entry) for entry in entries} == expected


@pytest.mark.parametrize(
    ("template", "key", "name", "value", "error"),
    [
        ("sample_template.pdf", "test", "readonly", None, TypeError),
        ("sample_template.pdf", "test", "required", None, TypeError),
        ("sample_template.pdf", "test", "hidden", None, TypeError),
        ("sample_template.pdf", "test", "multiline", None, TypeError),
        ("sample_template.pdf", "test", "comb", None, TypeError),
        ("sample_template.pdf", "test", "font", None, TypeError),
        ("sample_template.pdf", "test", "font_size", None, TypeError),
        ("sample_template.pdf", "test", "font_color", None, TypeError),
        ("sample_template.pdf", "test", "max_length", 0, ValueError),
        ("sample_template.pdf", "test", "max_length", -1, ValueError),
        ("sample_template.pdf", "test", "alignment", 3, ValueError),
        ("sample_template.pdf", "test", "alignment", -1, ValueError),
        ("sample_template_with_radio_button.pdf", "radio_1", "x", None, TypeError),
        ("sample_template_with_radio_button.pdf", "radio_1", "x", [1, 2], TypeError),
        *[
            (
                os.path.join("dropdown", "sample_template_with_dropdown.pdf"),
                "dropdown_1",
                name,
                None,
                TypeError,
            )
            for name in ("choices", "font", "font_size", "font_color")
        ],
    ],
)
def test_reject_property_value_not_stored_in_pdf(
    pdf_samples, template, key, name, value, error, assert_widgets_match_output
):
    obj = PdfWrapper(os.path.join(pdf_samples, template))
    expected = obj.read()
    widget = obj.widgets[key]
    state = dict(vars(widget))

    with pytest.raises(error, match=rf"'{key}'|Geometry values"):
        setattr(widget, name, value)

    assert vars(widget) == state
    assert not widget.hooks_to_trigger
    assert obj.read() == expected
    assert_widgets_match_output(obj)


@pytest.mark.parametrize(
    ("name", "entry", "parent", "value"),
    [
        ("max_length", "/MaxLen", 1, 10),
        ("alignment", "/Q", 1, 2),
        ("tooltip", "/TU", "field tooltip", "own tooltip"),
    ],
)
def test_clear_property_of_parent_field(
    sample_template_with_full_key,
    name,
    entry,
    parent,
    value,
    assert_widgets_match_output,
):
    # the widget of "Date mois" has no name, so its parent is the field
    stream = set_parent_entry(sample_template_with_full_key, "Date mois", entry, parent)
    assert find_widget(stream, "Date mois").get_inherited(entry) == parent

    obj = PdfWrapper(stream)
    setattr(obj.widgets["Date mois"], name, value)
    assert find_widget(obj.read(), "Date mois").get_inherited(entry) == value

    setattr(obj.widgets["Date mois"], name, None)
    assert find_widget(obj.read(), "Date mois").get_inherited(entry) is None
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize(
    ("name", "entry", "parent", "value"),
    [
        ("max_length", "/MaxLen", 1, 5),
        ("alignment", "/Q", 1, 2),
    ],
)
def test_clear_property_set_by_shared_parent(
    template_stream,
    name,
    entry,
    parent,
    value,
    use_full_widget_name,
    assert_widgets_match_output,
):
    stream = group_fields(template_stream, ("test", "test_2"), entry, parent)
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    widget = obj.widgets["group.test" if use_full_widget_name else "test"]
    # a value of its own is set on the widget, leaving the parent's
    setattr(widget, name, value)
    expected = obj.read()
    assert find_widget(expected, "test").get_inherited(entry) == value

    setattr(widget, name, None)
    # removing it from the parent would change "test_2" too
    with pytest.raises(ValueError, match=f"Cannot remove {entry}"):
        obj.read()

    assert getattr(widget, name) == value
    assert not widget.hooks_to_trigger
    assert obj.read() == expected
    assert find_widget(expected, "test_2").get_inherited(entry) == parent
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_tooltip_of_shared_parent_is_not_inherited(
    template_stream, use_full_widget_name, assert_widgets_match_output
):
    stream = group_fields(template_stream, ("test", "test_2"), "/TU", "shared tooltip")
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    widget = obj.widgets["group.test" if use_full_widget_name else "test"]
    # the tooltip is the alternate name of "group", not of its kids
    assert widget.tooltip is None

    widget.tooltip = "own tooltip"
    assert find_widget(obj.read(), "test")["/TU"] == "own tooltip"
    widget.tooltip = None
    output = obj.read()

    assert "/TU" not in find_widget(output, "test")
    assert find_widget(output, "test")["/Parent"]["/TU"] == "shared tooltip"
    assert_widgets_match_output(obj)


def test_tooltip_of_field_and_its_widget(
    sample_template_with_full_key, assert_widgets_match_output
):
    # the widget of "Date mois" has no name, so its parent is the field
    stream = set_parent_entry(
        sample_template_with_full_key, "Date mois", "/TU", "field tooltip"
    )
    obj = PdfWrapper(stream)
    assert obj.widgets["Date mois"].tooltip == "field tooltip"

    # a new tooltip goes to the field, which every widget of it reads
    obj.widgets["Date mois"].tooltip = "new tooltip"
    annot = find_widget(obj.read(), "Date mois")
    assert "/TU" not in annot
    assert annot["/Parent"]["/TU"] == "new tooltip"
    assert_widgets_match_output(obj)

    # one on the widget, as earlier versions wrote it, is read first and changed
    with Pdf.open(BytesIO(stream)) as pdf:
        for page in pdf.pages:
            for each in page.get("/Annots", []):
                if str(each.get("/Parent", {}).get("/T")) == "Date mois":
                    each.TU = String("widget tooltip")
        stream = save(pdf)
    obj = PdfWrapper(stream)
    assert obj.widgets["Date mois"].tooltip == "widget tooltip"
    obj.widgets["Date mois"].tooltip = "new tooltip"
    annot = find_widget(obj.read(), "Date mois")
    assert annot["/TU"] == "new tooltip"
    assert annot["/Parent"]["/TU"] == "field tooltip"


def test_null_tooltip(template_stream):
    # a null tooltip is absent
    stream = set_null_entries(template_stream, {"test": ["/TU"]})
    assert PdfWrapper(stream).widgets["test"].tooltip is None


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize(
    ("name", "entry", "chosen", "other", "new"), TEXT_FIELD_ENTRIES
)
@pytest.mark.parametrize(
    ("holders", "found"),
    [
        ((), None),
        # the AcroForm's /Q is the form's default, not the field's alignment
        (("/AcroForm",), None),
        (("/AcroForm", "outer"), "outer"),
        (("/AcroForm", "outer", "inner"), "inner"),
        # the widget's own entry takes precedence over its fields'
        (("/AcroForm", "inner", "test"), "test"),
    ],
    ids=["none", "acroform", "grandparent", "parent", "widget"],
)
def test_change_inherited_text_field_entry(
    template_stream,
    holders,
    found,
    name,
    entry,
    chosen,
    other,
    new,
    use_full_widget_name,
    assert_widgets_match_output,
):
    # the lowest holder has the chosen value, and the ones above it another
    values = {holder: chosen if holder == holders[-1] else other for holder in holders}
    stream = nest_fields(template_stream, values, entry)
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    key, other_key = (
        ("outer.inner.test", "outer.inner.test_2")
        if use_full_widget_name
        else ("test", "test_2")
    )
    # "test_2" inherits from "inner" and "outer" only
    shared = {None: None, "outer": chosen, "inner": chosen, "test": other}[found]
    assert getattr(obj.widgets[key], name) == (chosen if found else None)
    assert getattr(obj.widgets[other_key], name) == shared

    setattr(obj.widgets[key], name, new)
    result = obj.read()

    # only the widget's own field changes; fields shared with "test_2" and the
    # AcroForm don't
    assert get_nested_entries(result, entry) == {
        "test": new,
        "test_2": None,
        "inner": values.get("inner"),
        "outer": values.get("outer"),
        "/AcroForm": values.get("/AcroForm"),
    }
    reopened = PdfWrapper(result, use_full_widget_name=use_full_widget_name)
    assert getattr(reopened.widgets[key], name) == new
    assert getattr(reopened.widgets[other_key], name) == shared
    assert_widgets_match_output(obj)


@pytest.mark.parametrize(
    ("name", "entry", "chosen", "other", "new"), TEXT_FIELD_ENTRIES
)
@pytest.mark.parametrize("holder", ["none", "field", "widget"])
def test_change_text_field_entry_of_kid_widget(
    sample_template_with_full_key,
    holder,
    name,
    entry,
    chosen,
    other,
    new,
    assert_widgets_match_output,
):
    # the widget of "Date mois" has no name, so its parent is the field
    with Pdf.open(BytesIO(sample_template_with_full_key)) as pdf:
        for page in pdf.pages:
            for annot in page.get("/Annots", []):
                if "/Parent" in annot and str(annot.Parent.get("/T")) == "Date mois":
                    for each in (annot, annot.Parent):
                        if entry in each:
                            del each[entry]
                    if holder == "field":
                        annot.Parent[entry] = chosen
                    elif holder == "widget":
                        annot.Parent[entry] = other
                        annot[entry] = chosen
        stream = save(pdf)

    obj = PdfWrapper(stream)
    assert getattr(obj.widgets["Date mois"], name) == (
        None if holder == "none" else chosen
    )
    setattr(obj.widgets["Date mois"], name, new)
    widget = find_widget(obj.read(), "Date mois")

    # the value that was found changes, and without one, the field gets it
    assert widget.get(entry) == (new if holder == "widget" else None)
    assert widget["/Parent"].get_object().get(entry) == (
        other if holder == "widget" else new
    )
    assert_widgets_match_output(obj)


def test_read_max_length_of_kid_widget(sample_template_with_full_key):
    # the widget of "Date mois" has no name, and its field allows 2 characters
    obj = PdfWrapper(sample_template_with_full_key)

    assert obj.widgets["Date mois"].max_length == 2
    assert obj.schema["properties"]["Date mois"]["maxLength"] == 2
    assert obj.sample_data["Date mois"] == "Da"


@pytest.mark.parametrize(
    ("name", "entry", "chosen", "new"),
    [(name, entry, chosen, new) for name, entry, chosen, _, new in TEXT_FIELD_ENTRIES],
)
@pytest.mark.parametrize("clear", [False, True], ids=["set", "clear"])
def test_change_text_field_entry_with_parent_cycle(
    template_stream,
    name,
    entry,
    chosen,
    new,
    clear,
    assert_widgets_match_output,
):
    obj = PdfWrapper(with_parent_cycle(template_stream, "test"))
    # the cycle is reached before the entry, which reads as unset
    assert getattr(obj.widgets["test"], name) is None
    original = obj.read()
    # applied before the failing change, and discarded with it
    obj.widgets["test_2"].alignment = 2
    setattr(obj.widgets["test"], name, None if clear else new)

    with pytest.raises(ValueError, match="the /Parent chain of the field has a cycle"):
        obj.read()

    assert obj.widgets["test_2"].alignment is None
    assert getattr(obj.widgets["test"], name) is None
    assert not obj.widgets["test"].hooks_to_trigger
    assert not obj.widgets["test_2"].hooks_to_trigger
    assert obj.read() == original
    assert_widgets_match_output(obj)

    # the field's own value is found before the cycle
    with Pdf.open(BytesIO(original)) as pdf:
        get_field(pdf, "test")[entry] = chosen
        obj = PdfWrapper(save(pdf))
    assert getattr(obj.widgets["test"], name) == chosen
    setattr(obj.widgets["test"], name, new)

    assert find_widget(obj.read(), "test")[entry] == new


def test_clear_alignment_below_unnamed_parent_cycle(template_stream):
    # "test" loses its name, and its parent, which has none, is its own parent
    with Pdf.open(BytesIO(template_stream)) as pdf:
        field = get_field(pdf, "test")
        parent = pdf.make_indirect(Dictionary({"/Kids": Array([field])}))
        parent.Parent = parent
        field.Parent = parent
        field.Q = 1
        del field["/T"]
        stream = save(pdf)

    # with full names, the widget's key is empty
    obj = PdfWrapper(stream, use_full_widget_name=True)
    original = obj.read()
    assert obj.widgets[""].alignment == 1
    obj.widgets[""].alignment = None

    with pytest.raises(ValueError, match="Cannot remove /Q: the /Parent chain"):
        obj.read()

    assert obj.widgets[""].alignment == 1
    assert obj.read() == original


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize(
    ("name", "entry", "shared", "value"),
    [
        ("alignment", "/Q", 2, 1),
        ("max_length", "/MaxLen", 5, 9),
        ("readonly", "/Ff", 0, True),
        ("font_size", "/DA", "/Cour 9 Tf 0 g", 20),
    ],
)
def test_change_below_unnamed_field_keeps_shared_parent(
    template_stream, name, entry, shared, value, use_full_widget_name
):
    stream = below_unnamed_field(template_stream, entry, shared)
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    # without a name, the key is the unnamed field's, empty with full names
    key, other = ("", "outer.test_2") if use_full_widget_name else (None, "test_2")
    before = getattr(obj.widgets[other], name)

    # the change goes to the unnamed field, the widget's own field
    setattr(obj.widgets[key], name, value)
    reopened = PdfWrapper(obj.read(), use_full_widget_name=use_full_widget_name)
    assert getattr(reopened.widgets[key], name) == value
    assert getattr(reopened.widgets[other], name) == before
    with Pdf.open(BytesIO(obj.read())) as pdf:
        outer = get_field(pdf, "outer")
        assert entry in outer.Kids[0]
        assert outer[entry] == pdf_value(shared)


@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_clear_entry_below_unnamed_field(template_stream, use_full_widget_name):
    key = "" if use_full_widget_name else None
    # "outer", shared with "test_2", sets the alignment, which can't be removed
    stream = below_unnamed_field(template_stream, "/Q", 2)
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    original = obj.read()
    obj.widgets[key].alignment = None
    with pytest.raises(ValueError, match="Cannot remove /Q: a parent field"):
        obj.read()
    assert obj.read() == original

    # the unnamed field's own tooltip is removed, and "outer" keeps its own
    stream = below_unnamed_field(template_stream, "/TU", "outer tooltip")
    with Pdf.open(BytesIO(stream)) as pdf:
        get_field(pdf, "outer").Kids[0].TU = String("own tooltip")
        stream = save(pdf)
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert obj.widgets[key].tooltip == "own tooltip"
    obj.widgets[key].tooltip = None
    with Pdf.open(BytesIO(obj.read())) as pdf:
        outer = get_field(pdf, "outer")
        assert "/TU" not in outer.Kids[0]
        assert outer.TU == "outer tooltip"


@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_change_choices_below_unnamed_field(
    sample_template_with_dropdown, use_full_widget_name
):
    # "dropdown_1" becomes an unnamed field with an unnamed widget, below
    # "outer", whose options "sibling" shares
    with Pdf.open(BytesIO(sample_template_with_dropdown)) as pdf:
        field = get_field(pdf, "dropdown_1")
        sibling = pdf.make_indirect(Dictionary(field))
        sibling.T = String("sibling")
        del sibling["/Opt"]
        pdf.pages[0].Annots.append(sibling)
        split_widgets(pdf, field)
        del field["/T"]
        del field["/Opt"]
        outer = pdf.make_indirect(
            Dictionary(
                {
                    "/T": String("outer"),
                    "/Opt": Array(["shared"]),
                    "/Kids": Array([field, sibling]),
                }
            )
        )
        field.Parent = outer
        sibling.Parent = outer
        pdf.Root.AcroForm.Fields = Array(
            [each for each in pdf.Root.AcroForm.Fields if each != field] + [outer]
        )
        stream = save(pdf)

    key, other = ("", "outer.sibling") if use_full_widget_name else (None, "sibling")
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert obj.widgets[key].choices == obj.widgets[other].choices == ("shared",)

    obj.widgets[key].choices = ["new"]
    reopened = PdfWrapper(obj.read(), use_full_widget_name=use_full_widget_name)
    assert reopened.widgets[key].choices == ("new",)
    assert reopened.widgets[other].choices == ("shared",)
