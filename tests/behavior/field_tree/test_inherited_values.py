# -*- coding: utf-8 -*-

from io import BytesIO
from unittest.mock import patch

import pytest
from pikepdf import Array, Dictionary, Name, Pdf, String
from pypdf import PdfReader

from PyPDFForm import BlankPage, Fields, PdfWrapper
from PyPDFForm.lib.constants import RADIO, READ_ONLY
from PyPDFForm.lib.middleware.checkbox import Checkbox
from PyPDFForm.lib.middleware.radio import Radio
from tests.support.builders import (
    get_field,
    nest_fields,
    put_under_outer,
    save,
    set_null_entries,
    split_widgets,
    with_fields_above,
    with_parent_cycle,
)
from tests.support.checks import find_widget, get_nested_entries, get_widget_states


def test_field_below_widget_inherits_nothing_from_it(
    template_stream, assert_widgets_match_output
):
    # "test_2" gets the /Parent "test", a text field merged with its widget
    with Pdf.open(BytesIO(template_stream)) as pdf:
        test, test_2 = get_field(pdf, "test"), get_field(pdf, "test_2")
        test_2.Parent = test
        test.Q = 2
        test.MaxLen = 5
        test.Ff = READ_ONLY
        test.DA = String("/Cour 20 Tf 1 0 0 rg")
        del test_2["/DA"]
        pdf.Root.AcroForm.DA = String("/Helv 9 Tf 0 g")
        stream = save(pdf)

    obj = PdfWrapper(stream)
    test_2 = obj.widgets["test_2"]
    # "test" is a field of its own, not one above "test_2"
    assert (test_2.alignment, test_2.max_length, test_2.readonly) == (None, None, False)
    assert (test_2.font, test_2.font_size, test_2.font_color) == ("/Helv", 9, (0, 0, 0))
    assert obj.widgets["test"].alignment == 2

    # changes go to "test_2", and "test" keeps its entries
    test_2.alignment = 1
    test_2.font_size = 12
    output = obj.read()
    assert find_widget(output, "test_2")["/Q"] == 1
    assert find_widget(output, "test_2")["/DA"] == "/Helv 12 Tf 0 g"
    assert find_widget(output, "test")["/Q"] == 2
    assert find_widget(output, "test")["/DA"] == "/Cour 20 Tf 1 0 0 rg"
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize(
    ("holder", "value"),
    [
        ("parent", True),
        ("grandparent", True),
        # the cycle is reached before a value is found
        ("cycle", None),
    ],
)
def test_checkbox_value_inherited_from_field_above(
    template_stream, holder, value, use_full_widget_name, assert_widgets_match_output
):
    # "group" is a button field, so "check" is a checkbox
    stream = with_fields_above(template_stream, {"/DV": Name.Yes}, holder)

    # the value is inherited through the field hierarchy
    key = "outer.group.check" if use_full_widget_name else "check"
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert type(obj.widgets[key]) is Checkbox
    assert obj.data[key] is value

    # a value of its own takes precedence
    obj.fill({key: not value})
    result = obj.read()
    state = "/Off" if value else "/Yes"
    assert get_widget_states(result, "check") == [[state, state]]
    reopened = PdfWrapper(result, use_full_widget_name=use_full_widget_name)
    assert reopened.data[key] is (None if value else True)
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize(
    ("holder", "value"),
    [
        ("parent", 0),
        ("grandparent", 0),
        # the cycle is reached before a value is found
        ("cycle", None),
    ],
)
def test_radio_value_inherited_from_field_above(
    template_stream, holder, value, use_full_widget_name, assert_widgets_match_output
):
    # "group" sets the radio flag, which "check", without /Ff of its own,
    # inherits
    stream = with_fields_above(template_stream, {"/Ff": RADIO}, holder)

    # it is a radio group with one option, whose value is inherited through
    # the field hierarchy
    key = "outer.group.check" if use_full_widget_name else "check"
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert type(obj.widgets[key]) is Radio
    assert obj.widgets[key].number_of_options == 1
    assert obj.data[key] == value

    # selecting it writes a value of its own, and the fields above keep theirs
    obj.fill({key: 0})
    result = obj.read()
    assert get_widget_states(result, "check") == [["/Yes", "/Yes"]]
    group = find_widget(result, "check")["/Parent"].get_object()
    assert group.get("/V") == ("/Yes" if holder == "parent" else None)
    assert group["/Parent"].get_object().get("/V") == (
        "/Yes" if holder == "grandparent" else None
    )
    reopened = PdfWrapper(result, use_full_widget_name=use_full_widget_name)
    assert reopened.data[key] == 0
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_radio_group_value_inherited_from_field_above(
    template_with_radiobutton_stream, use_full_widget_name, assert_widgets_match_output
):
    # "radio_1", without a value of its own, is a kid of "outer", which has the
    # value of its second option
    with Pdf.open(BytesIO(template_with_radiobutton_stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        radio = get_field(pdf, "radio_1")
        outer = pdf.make_indirect(
            Dictionary(
                {"/T": String("outer"), "/V": Name("/1"), "/Kids": Array([radio])}
            )
        )
        radio.Parent = outer
        radio.Kids[1].AS = Name("/1")
        pdf.Root.AcroForm.Fields = Array(
            [field for field in fields if field != radio] + [outer]
        )
        stream = save(pdf)

    key = "outer.radio_1" if use_full_widget_name else "radio_1"
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert obj.data[key] == 1

    # selecting another option writes the group's own value
    obj.fill({key: 0})
    result = obj.read()
    assert get_widget_states(result, "radio_1") == [["/0", None], ["/Off", None]]
    radio = find_widget(result, "radio_1")["/Parent"].get_object()
    assert radio["/V"] == "/0"
    assert radio["/Parent"].get_object()["/V"] == "/1"
    assert PdfWrapper(result, use_full_widget_name=use_full_widget_name).data[key] == 0
    assert_widgets_match_output(obj)


def test_null_checkbox_value(template_stream):
    # a null value is absent, so the checkbox isn't checked
    stream = set_null_entries(template_stream, {"check": ["/V"]})
    assert PdfWrapper(stream).widgets["check"].value is None


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ({"outer": "outer value"}, "outer value"),
        ({"inner": "inner value", "outer": "outer value"}, "inner value"),
        ({"test": "own value", "outer": "outer value"}, "own value"),
    ],
)
def test_inherited_text_value(
    template_stream, values, expected, use_full_widget_name, assert_widgets_match_output
):
    stream = nest_fields(template_stream, values, "/V")
    key, other = (
        ("outer.inner.test", "outer.inner.test_2")
        if use_full_widget_name
        else ("test", "test_2")
    )
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert obj.widgets[key].value == expected
    assert obj.widgets[other].value == values.get("inner", values["outer"])

    # a fill writes the field's own value, so the fields above keep theirs
    obj.fill({key: "filled"})
    entries = get_nested_entries(obj.read(), "/V")
    assert entries["test"] == "filled"
    assert entries["inner"] == values.get("inner")
    assert entries["outer"] == values["outer"]
    assert obj.widgets[other].value == values.get("inner", values["outer"])
    assert_widgets_match_output(obj)


def test_inherited_text_value_null_and_cycle(template_stream):
    # a null value is absent, so the value above it is read
    stream = set_null_entries(
        nest_fields(template_stream, {"outer": "outer value"}, "/V"), {"test": ["/V"]}
    )
    assert PdfWrapper(stream).widgets["test"].value == "outer value"

    # a cycle before any value reads as no value
    obj = PdfWrapper(with_parent_cycle(template_stream, "test"))
    assert obj.widgets["test"].value is None
    obj.fill({"test": "foo"})
    assert PdfWrapper(obj.read()).widgets["test"].value == "foo"


@pytest.mark.parametrize(
    ("entries", "expected"),
    [
        # the value is inherited, and the indices aren't
        ({"/V": "bar"}, 1),
        ({"/V": "foo", "/I": Array([1])}, 0),
        ({"/V": "absent"}, None),
    ],
)
def test_inherited_dropdown_value(
    sample_template_with_dropdown, entries, expected, assert_widgets_match_output
):
    stream = put_under_outer(sample_template_with_dropdown, ("dropdown_1",), entries)
    obj = PdfWrapper(stream)
    assert obj.widgets["dropdown_1"].value == expected

    obj.fill({"dropdown_1": 2})
    field = find_widget(obj.read(), "dropdown_1")
    assert field["/V"] == "foobar"
    assert field["/Parent"]["/V"] == entries["/V"]
    assert_widgets_match_output(obj)


@pytest.mark.parametrize(
    ("holder", "expected"),
    [
        # the field's own options, then the ones it inherits
        ("own", ("x", "y")),
        ("outer", ("a", "b")),
        # a kid widget inherits them through its field
        ("kid", ("a", "b")),
        # options an earlier version wrote on a kid widget are still read
        ("widget", ("w",)),
    ],
)
def test_inherited_dropdown_choices(
    sample_template_with_dropdown, holder, expected, assert_widgets_match_output
):
    stream = put_under_outer(
        sample_template_with_dropdown, ("dropdown_1",), {"/Opt": Array(["a", "b"])}
    )
    with Pdf.open(BytesIO(stream)) as pdf:
        field = get_field(pdf, "outer").Kids[0]
        if holder == "own":
            field.Opt = Array(["x", "y"])
        elif holder in ("kid", "widget"):
            (widget,) = split_widgets(pdf, field)
            if holder == "widget":
                widget.Opt = Array(["w"])
        stream = save(pdf)

    obj = PdfWrapper(stream)
    assert obj.widgets["dropdown_1"].choices == expected

    # new options replace the ones found on the widget or its field, or go
    # to its field, so its other widgets get them, and "outer" keeps its own
    obj.widgets["dropdown_1"].choices = ["new"]
    annot = find_widget(obj.read(), "dropdown_1")
    if holder in ("own", "outer"):
        # the field is merged with its widget
        assert len(annot["/Opt"]) == 1
        outer = annot["/Parent"]
    else:
        field, outer = annot["/Parent"], annot["/Parent"]["/Parent"]
        changed, unchanged = (annot, field) if holder == "widget" else (field, annot)
        assert len(changed["/Opt"]) == 1
        assert "/Opt" not in unchanged
    assert [str(each) for each in outer["/Opt"]] == ["a", "b"]
    assert PdfWrapper(obj.read()).widgets["dropdown_1"].choices == ("new",)
    assert_widgets_match_output(obj)


def test_dropdown_choices_null_malformed_and_cycle(sample_template_with_dropdown):
    stream = put_under_outer(
        sample_template_with_dropdown, ("dropdown_1",), {"/Opt": Array(["a", "b"])}
    )
    # a null /Opt is absent, so the options above it are read
    null = set_null_entries(stream, {"dropdown_1": ["/Opt"]})
    assert PdfWrapper(null).widgets["dropdown_1"].choices == ("a", "b")

    # options that aren't an array are no options
    with Pdf.open(BytesIO(stream)) as pdf:
        get_field(pdf, "outer").Kids[0].Opt = Name("/foo")
        malformed = save(pdf)
    assert PdfWrapper(malformed).widgets["dropdown_1"].choices == ()

    # a cycle before any options reads as none, and changing them raises
    with Pdf.open(BytesIO(sample_template_with_dropdown)) as pdf:
        field = get_field(pdf, "dropdown_1")
        del field["/Opt"]
        parent = pdf.make_indirect(Dictionary({"/Kids": Array([field])}))
        parent.Parent = parent
        field.Parent = parent
        cycle = save(pdf)
    obj = PdfWrapper(cycle)
    original = obj.read()
    assert obj.widgets["dropdown_1"].choices == ()
    obj.widgets["dropdown_1"].choices = ["new"]

    with pytest.raises(ValueError, match="the /Parent chain of the field has a cycle"):
        obj.read()
    assert obj.widgets["dropdown_1"].choices == ()
    assert obj.read() == original


@pytest.mark.parametrize("own", [True, False], ids=["own", "inherited"])
def test_clearing_dropdown_value_set_above_raises(
    sample_template_with_dropdown, own, assert_widgets_match_output
):
    # "dropdown_1" selects "bar", its own value below the "foo" of "outer",
    # or the value it inherits from "outer"
    stream = put_under_outer(
        sample_template_with_dropdown, ("dropdown_1",), {"/V": "foo" if own else "bar"}
    )
    if own:
        with Pdf.open(BytesIO(stream)) as pdf:
            get_field(pdf, "outer").Kids[0].V = String("bar")
            stream = save(pdf)
    obj = PdfWrapper(stream)
    original = obj.read()
    assert obj.data["dropdown_1"] == 1

    # the new choices don't have "bar", but "outer", which other fields can
    # share, would still give the field a value
    obj.widgets["dropdown_1"].choices = ["foo", "x"]
    assert obj.data["dropdown_1"] is None
    with pytest.raises(
        ValueError, match="Cannot remove /V: a parent field shared with other fields"
    ):
        obj.read()

    assert obj.widgets["dropdown_1"].choices == ("foo", "bar", "foobar", " ")
    assert obj.data["dropdown_1"] == 1
    assert obj.read() == original
    assert_widgets_match_output(obj)

    # filling no value raises too, but filling a value gives the field one of
    # its own, and removing it leaves nothing to inherit
    obj.widgets["dropdown_1"].choices = ["foo", "x"]
    with pytest.raises(ValueError, match="Cannot remove /V"):
        obj.fill({"dropdown_1": None})
    obj.widgets["dropdown_1"].choices = ["foo", "x"]
    output = obj.fill({"dropdown_1": 1}).read()
    assert obj.data["dropdown_1"] == PdfWrapper(output).data["dropdown_1"] == 1
    assert find_widget(output, "dropdown_1")["/V"] == "x"
    assert_widgets_match_output(obj)

    # so does a value assigned on the widget, which filling writes, also
    # when it is the value of "outer"
    for value in (1, 0):
        obj = PdfWrapper(stream)
        obj.widgets["dropdown_1"].choices = ["foo", "x"]
        obj.widgets["dropdown_1"].value = value
        output = obj.fill({}).read()
        assert obj.data["dropdown_1"] == PdfWrapper(output).data["dropdown_1"] == value
        assert find_widget(output, "dropdown_1")["/V"] == ("foo", "x")[value]

    obj = PdfWrapper(stream)
    obj.widgets["dropdown_1"].choices = ["foo", "x"]
    assert (
        "dropdown_1" not in PdfWrapper(obj.remove_fields(["dropdown_1"]).read()).widgets
    )


def test_fill_keeps_value_set_above_of_field_with_short_name(
    assert_widgets_match_output,
):
    # "billing.choice" selects Apple below the "Banana" of "billing", and
    # "shipping.choice", whose widget comes later and has the key, Pear
    created = (
        PdfWrapper(BlankPage())
        .bulk_create_fields(
            [
                Fields.DropdownField(
                    name, 1, 20, y, options=["Apple", "Banana", "Pear"]
                )
                for name, y in (("billing", 20), ("shipping", 60))
            ]
        )
        .fill({"billing": 0, "shipping": 2})
        .read()
    )
    with Pdf.open(BytesIO(created)) as pdf:
        fields = []
        for name in ("billing", "shipping"):
            field = get_field(pdf, name)
            field.T = String("choice")
            parent = pdf.make_indirect(
                Dictionary({"/T": String(name), "/Kids": Array([field])})
            )
            if name == "billing":
                parent.V = String("Banana")
            field.Parent = parent
            fields.append(parent)
        pdf.Root.AcroForm.Fields = Array(fields)
        stream = save(pdf)
    obj = PdfWrapper(stream)
    original = obj.read()

    # the new choices clear "billing.choice", which would inherit Banana;
    # filling doesn't write the key's Pear, which didn't change, so it
    # raises as reading does, and changes nothing
    obj.widgets["choice"].choices = ["Banana", "Pear"]
    with pytest.raises(ValueError, match="Cannot remove /V"):
        obj.fill({})
    with pytest.raises(ValueError, match="Cannot remove /V"):
        obj.read()
    assert obj.read() == original
    assert PdfWrapper(original, use_full_widget_name=True).data == {
        "billing.choice": 0,
        "shipping.choice": 2,
    }
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("title", ["outer.dropdown_1", "dropdown_1"])
@pytest.mark.parametrize(
    "operation",
    [
        lambda obj: obj.fill({"dropdown_1": 1}),
        lambda obj: obj.remove_fields(["dropdown_1"]),
        lambda obj: (setattr(obj.widgets["dropdown_1"], "value", 0), obj.fill({}))[1],
    ],
    ids=["fill", "remove_fields", "assigned"],
)
def test_note_with_field_name_doesnt_block_new_choices(
    sample_template_with_dropdown, title, operation
):
    # "dropdown_1" selects its own "bar" below the "foo" of "outer", and a
    # note has its full or short name as its title
    stream = put_under_outer(
        sample_template_with_dropdown, ("dropdown_1",), {"/V": "foo"}
    )
    with Pdf.open(BytesIO(stream)) as pdf:
        get_field(pdf, "outer").Kids[0].V = String("bar")
        note = Dictionary(
            {
                "/Type": Name.Annot,
                "/Subtype": Name.Text,
                "/Rect": Array([300, 300, 320, 320]),
                "/T": String(title),
            }
        )
        pdf.pages[0].Annots.append(pdf.make_indirect(note))
        stream = save(pdf)
    obj = PdfWrapper(stream)

    # the note is no widget, so it doesn't count as the field
    obj.widgets["dropdown_1"].choices = ["foo", "x"]
    output = operation(obj).read()
    assert PdfWrapper(output).data == obj.data


def test_cleared_selections_are_checked_in_one_read(sample_template_with_dropdown):
    # "dropdown_1" and a copy of it, "dropdown_2", select their own "bar"
    # below the "foo" of "outer"
    with Pdf.open(BytesIO(sample_template_with_dropdown)) as pdf:
        field = get_field(pdf, "dropdown_1")
        copy = pdf.make_indirect(Dictionary(field))
        copy.T = String("dropdown_2")
        copy.Rect = Array([300, 300, 400, 320])
        pdf.pages[0].Annots.append(copy)
        pdf.Root.AcroForm.Fields.append(copy)
        stream = save(pdf)
    stream = put_under_outer(stream, ("dropdown_1", "dropdown_2"), {"/V": "foo"})
    with Pdf.open(BytesIO(stream)) as pdf:
        for kid in get_field(pdf, "outer").Kids:
            kid.V = String("bar")
        stream = save(pdf)
    obj = PdfWrapper(stream)
    for key in ("dropdown_1", "dropdown_2"):
        obj.widgets[key].choices = ["foo", "x"]

    # the output is read once to check both fields
    with patch("PyPDFForm.lib.hooks.PdfReader", wraps=PdfReader) as reader:
        output = obj.fill({"dropdown_1": 1, "dropdown_2": 1}).read()
    assert reader.call_count == 1
    assert PdfWrapper(output).data == {**obj.data, "dropdown_1": 1, "dropdown_2": 1}


@pytest.mark.parametrize(
    ("operation", "target"),
    [
        (lambda obj: obj.fill({"dropdown_1": 1}), "PyPDFForm.lib.wrapper.fill"),
        (
            lambda obj: obj.remove_fields(["dropdown_1"]),
            "PyPDFForm.lib.wrapper.remove_widgets_by_keys",
        ),
    ],
    ids=["fill", "remove_fields"],
)
def test_failed_operation_keeps_dropdown_value_set_above(
    sample_template_with_dropdown, operation, target, assert_widgets_match_output
):
    # "dropdown_1" selects its own "bar" below the "foo" of "outer"
    stream = put_under_outer(
        sample_template_with_dropdown, ("dropdown_1",), {"/V": "foo"}
    )
    with Pdf.open(BytesIO(stream)) as pdf:
        get_field(pdf, "outer").Kids[0].V = String("bar")
        stream = save(pdf)
    obj = PdfWrapper(stream)
    original = obj.read()
    obj.widgets["dropdown_1"].choices = ["foo", "x"]
    stored = getattr(obj, "_stream")

    # the operation would clear the selection without raising, but fails, so
    # the PDF is unchanged and the choices are still queued
    with patch(target, side_effect=RuntimeError), pytest.raises(RuntimeError):
        operation(obj)
    assert getattr(obj, "_stream") == stored
    assert obj.data["dropdown_1"] is None
    assert [hook for hook, _ in obj.widgets["dropdown_1"].hooks_to_trigger] == [
        "update_dropdown_choices"
    ]

    # reading them alone still raises, and restores the selection
    with pytest.raises(ValueError, match="Cannot remove /V"):
        obj.read()
    assert obj.data["dropdown_1"] == 1
    assert obj.read() == original
    assert_widgets_match_output(obj)


def test_dropdown_choices_move_shared_selection_once(
    sample_template_with_dropdown, assert_widgets_match_output
):
    # the two widgets of "dropdown_1" share its selection, "foobar" at index 2
    filled = PdfWrapper(sample_template_with_dropdown).fill({"dropdown_1": 2}).read()
    with Pdf.open(BytesIO(filled)) as pdf:
        for widget in split_widgets(pdf, get_field(pdf, "dropdown_1"), count=2):
            if "/I" in widget:
                del widget["/I"]
        stream = save(pdf)
    obj = PdfWrapper(stream)
    assert obj.data["dropdown_1"] == 2

    # each widget gets both lists, but the selection moves once: it stays
    # at index 2, then takes the first "foobar"
    obj.widgets["dropdown_1"].choices = ["x", "foobar", "foobar"]
    obj.widgets["dropdown_1"].choices = ["foobar", "foobar"]
    output = obj.read()
    assert obj.data["dropdown_1"] == PdfWrapper(output).data["dropdown_1"] == 0
    assert find_widget(output, "dropdown_1")["/Parent"]["/I"] == [0]
    assert_widgets_match_output(obj)


def test_dropdown_choices_move_selection_of_last_widget(
    sample_template_with_dropdown, assert_widgets_match_output
):
    # the second widget of "dropdown_1", which the wrapper reads, has options
    # of its own, with the selected "bar" at index 0 instead of 1
    filled = PdfWrapper(sample_template_with_dropdown).fill({"dropdown_1": 1}).read()
    with Pdf.open(BytesIO(filled)) as pdf:
        widgets = split_widgets(pdf, get_field(pdf, "dropdown_1"), count=2)
        for widget in widgets:
            if "/I" in widget:
                del widget["/I"]
        widgets[1].Opt = Array([String("bar"), String("y")])
        stream = save(pdf)
    obj = PdfWrapper(stream)
    assert obj.widgets["dropdown_1"].choices == ("bar", "y")
    assert obj.data["dropdown_1"] == 0

    # both new options have "bar", so the selection keeps the index the
    # wrapper has
    obj.widgets["dropdown_1"].choices = [("B1", "bar"), ("B2", "bar")]
    output = obj.read()
    assert obj.data["dropdown_1"] == PdfWrapper(output).data["dropdown_1"] == 0
    assert_widgets_match_output(obj)
