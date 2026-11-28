# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from pikepdf import Array, Dictionary, Name, Pdf, String
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NullObject

from PyPDFForm import PdfArray, PdfWrapper
from PyPDFForm.lib.constants import PUSHBUTTON, RADIO
from PyPDFForm.lib.middleware.checkbox import Checkbox
from PyPDFForm.lib.middleware.dropdown import Dropdown
from PyPDFForm.lib.middleware.radio import Radio
from PyPDFForm.lib.middleware.signature import Signature
from PyPDFForm.lib.middleware.text import Text
from tests.support.builders import (
    build_button_group,
    checkbox_field,
    get_field,
    name_checkbox_like_radio_group,
    nest_fields,
    save,
    set_on_state,
    with_button_parent,
    with_field_cycle,
)
from tests.support.checks import (
    find_widget,
    get_checkbox_and_radio_states,
    get_checkbox_field_states,
    get_widget_states,
)


@pytest.mark.parametrize("default", [Name.Off, Name.Yes])
@pytest.mark.parametrize("on_index", [0, 1, None])
def test_radio_group_with_off_or_yes_default_is_radio(default, on_index):
    form = PdfWrapper(build_button_group(49152, default, on_index))

    widget = form.widgets["group"]
    assert isinstance(widget, Radio)
    assert widget.number_of_options == 2
    assert isinstance(form.pages[0].widgets["group"], Radio)

    assert PdfWrapper(form.fill({"group": 1}).read()).data["group"] == 1


def test_radio_group_with_off_value_stays_unselected():
    form = PdfWrapper(build_button_group(49152, Name.Off, None, Name.Off))
    assert form.data["group"] is None

    with Pdf.open(BytesIO(form.fill({}).read())) as pdf:
        field = pdf.Root.AcroForm.Fields[0]
        assert str(field.V) == "/Off"
        assert [str(kid.AS) for kid in field.Kids] == ["/Off", "/Off"]


def test_button_without_radio_flag_and_off_default_is_checkbox():
    widget = PdfWrapper(build_button_group(0, Name.Off, None)).widgets["group"]
    assert type(widget) is Checkbox


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize(
    ("holders", "expected"),
    [
        ({}, {"test": None, "test_2": None}),
        ({"outer": Name.Tx}, {"test": Text, "test_2": Text}),
        ({"inner": Name.Tx}, {"test": Text, "test_2": Text}),
        # the type of a lower field, or the widget's own, takes precedence
        ({"outer": Name.Sig, "inner": Name.Tx}, {"test": Text, "test_2": Text}),
        ({"inner": Name.Sig, "test": Name.Tx}, {"test": Text, "test_2": Signature}),
    ],
    ids=["none", "grandparent", "parent", "lower-field", "widget"],
)
def test_inherited_field_type(
    template_stream,
    holders,
    expected,
    use_full_widget_name,
    assert_widgets_match_output,
):
    obj = PdfWrapper(
        nest_fields(template_stream, holders, "/FT"),
        use_full_widget_name=use_full_widget_name,
    )
    prefix = "outer.inner." if use_full_widget_name else ""

    for name, _type in expected.items():
        widget = obj.widgets.get(prefix + name)
        assert (type(widget) if widget is not None else None) is _type

    if expected["test"] is Text:
        obj.fill({prefix + "test": "filled"})
        assert PdfWrapper(obj.read()).data["test"] == "filled"
        assert_widgets_match_output(obj)


@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_radio_group_with_inherited_field_type(
    template_with_radiobutton_stream, use_full_widget_name, assert_widgets_match_output
):
    # "radio_1" is a kid of "outer", which has its /FT, and its options have none
    with Pdf.open(BytesIO(template_with_radiobutton_stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        radio = get_field(pdf, "radio_1")
        outer = pdf.make_indirect(
            Dictionary(
                {"/T": String("outer"), "/FT": Name.Btn, "/Kids": Array([radio])}
            )
        )
        radio.Parent = outer
        del radio["/FT"]
        pdf.Root.AcroForm.Fields = Array(
            [field for field in fields if field != radio] + [outer]
        )
        stream = save(pdf)

    key = "outer.radio_1" if use_full_widget_name else "radio_1"
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert isinstance(obj.widgets[key], Radio)
    assert obj.widgets[key].number_of_options == 2

    obj.fill({key: 1})
    result = obj.read()
    assert get_widget_states(result, "radio_1") == [["/Off", None], ["/1", None]]
    assert find_widget(result, "radio_1")["/Parent"].get_object()["/V"] == "/1"
    assert PdfWrapper(result, use_full_widget_name=use_full_widget_name).data[key] == 1
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("shape", ["group", "mutual", "listing", "three"])
@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_field_type_with_parent_cycle(template_stream, shape, use_full_widget_name):
    # no field of the cycle has a /FT, so the cycle is reached before one is found
    names = ("test", "test_2", "test_3") if shape == "three" else ("test", "test_2")
    with Pdf.open(BytesIO(with_field_cycle(template_stream, shape))) as pdf:
        for page in pdf.pages:
            for annot in page.Annots:
                if str(annot.get("/T")) in names:
                    del annot["/FT"]
        stream = save(pdf)

    # the fields of the cycle aren't widgets, and the others can be filled
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert not any(key.split(".")[-1] in names for key in obj.widgets)
    obj.fill({"check": True})
    assert PdfWrapper(obj.read()).data["check"] is True


@pytest.mark.parametrize(
    ("default", "_type"),
    [("/Yes", Checkbox), ("/Off", Checkbox), ("/0", Radio), (None, Radio)],
)
def test_inherited_default_value_tells_checkbox_from_radio(
    template_with_radiobutton_stream, default, _type
):
    # "radio_1" sets neither the radio flag nor a default value, and its
    # options don't repeat its field type, so the default it inherits decides
    with Pdf.open(BytesIO(template_with_radiobutton_stream)) as pdf:
        field = get_field(pdf, "radio_1")
        del field["/Ff"]
        outer = pdf.make_indirect(
            Dictionary({"/T": String("outer"), "/Kids": Array([field])})
        )
        if default is not None:
            outer.DV = Name(default)
        field.Parent = outer
        pdf.Root.AcroForm.Fields = Array(
            [each for each in pdf.Root.AcroForm.Fields if each != field] + [outer]
        )
        stream = save(pdf)

    assert type(PdfWrapper(stream).widgets["radio_1"]) is _type


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize(
    ("shape", "keys", "_type", "value", "expected"),
    [
        # a widget with a name is a field of its own, so it is a checkbox, and
        # its value and its parent's are independent
        (
            "named",
            ("check_2", "check.check_2"),
            Checkbox,
            True,
            {"check": [["/Off", None]], "check_2": [["/Yes", "/Yes"]]},
        ),
        (
            "named",
            ("check", "check"),
            Checkbox,
            True,
            {"check": [["/Yes", "/Yes"]], "check_2": [["/Off", None]]},
        ),
        # a widget without a name is an option of its field, which gets the
        # value, although the field doesn't list it
        (
            "unnamed",
            ("check", "check"),
            Radio,
            0,
            {"check": [["/Off", "/Yes"], ["/Yes", None]]},
        ),
        # "check" sets the radio flag, so it is a radio group with one option,
        # and filling it doesn't clear "check_2", a kid with a name
        (
            "cycle",
            ("check", "check_2.check"),
            Radio,
            0,
            {"check": [["/Yes", "/Yes"]], "check_2": [["/Off", None]]},
        ),
        # "check_2" doesn't inherit the flag from "check", a widget, so it is
        # a checkbox
        (
            "cycle",
            ("check_2", "check.check_2"),
            Checkbox,
            True,
            {"check": [["/Off", None]], "check_2": [["/Yes", "/Yes"]]},
        ),
    ],
    ids=["named-check_2", "named-check", "unnamed", "cycle-check", "cycle-check_2"],
)
def test_fill_button_widget_its_parent_does_not_list(
    template_stream,
    shape,
    keys,
    _type,
    value,
    expected,
    use_full_widget_name,
    assert_widgets_match_output,
):
    key = keys[use_full_widget_name]
    obj = PdfWrapper(
        with_button_parent(template_stream, shape),
        use_full_widget_name=use_full_widget_name,
    )
    assert type(obj.widgets[key]) is _type
    before = obj.data

    obj.fill({key: value})
    result = obj.read()
    for name, states in expected.items():
        assert get_widget_states(result, name) == states
    # every other field keeps its value
    reopened = PdfWrapper(result, use_full_widget_name=use_full_widget_name)
    assert reopened.data == {**before, key: value}
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize("shape", ["merged", "kids"])
@pytest.mark.parametrize("selected", [False, True])
def test_radio_button_with_name(
    template_stream, shape, selected, use_full_widget_name, assert_widgets_match_output
):
    # "check" and "check_2" set the radio flag ("merged") or inherit it from
    # "group", a radio field above them ("kids"), so each is a radio group whose
    # one option is the widget itself
    with Pdf.open(BytesIO(template_stream)) as pdf:
        check, check_2 = get_field(pdf, "check"), get_field(pdf, "check_2")
        if shape == "merged":
            check.Ff = check_2.Ff = RADIO
        else:
            group = pdf.make_indirect(
                Dictionary(
                    {
                        "/T": String("group"),
                        "/FT": Name.Btn,
                        "/Ff": RADIO,
                        "/Kids": Array([check, check_2]),
                    }
                )
            )
            check.Parent = check_2.Parent = group
            pdf.Root.AcroForm.Fields = Array(
                [
                    field
                    for field in pdf.Root.AcroForm.Fields
                    if field not in (check, check_2)
                ]
                + [group]
            )
        if selected:
            check.V = check.AS = Name.Yes
        stream = save(pdf)

    prefix = "group." if shape == "kids" and use_full_widget_name else ""
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    for name in ("check", "check_2"):
        assert isinstance(obj.widgets[prefix + name], Radio)
        assert obj.widgets[prefix + name].number_of_options == 1
    assert obj.widgets[prefix + "check"].value == (0 if selected else None)

    obj.fill({prefix + "check_2": 0})
    result = obj.read()
    # the widget gets the value, and the other field keeps its own
    assert get_widget_states(result, "check_2") == [["/Yes", "/Yes"]]
    assert get_widget_states(result, "check") == [
        ["/Yes", "/Yes"] if selected else ["/Off", None]
    ]
    if shape == "kids":
        assert "/V" not in find_widget(result, "check")["/Parent"].get_object()
    reopened = PdfWrapper(result, use_full_widget_name=use_full_widget_name)
    assert reopened.data[prefix + "check_2"] == 0
    assert reopened.data[prefix + "check"] == (0 if selected else None)
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("unlisted", [0, 1], ids=["first-unlisted", "last-unlisted"])
@pytest.mark.parametrize("indices", [(1, 0), (0, 1)], ids=["last-first", "first-last"])
def test_fill_radio_option_its_field_does_not_list(
    template_with_radiobutton_stream, unlisted, indices, assert_widgets_match_output
):
    # one option of "radio_1" isn't in its field's /Kids
    with Pdf.open(BytesIO(template_with_radiobutton_stream)) as pdf:
        radio = get_field(pdf, "radio_1")
        radio.Kids = Array([radio.Kids[1 - unlisted]])
        stream = save(pdf)

    obj = PdfWrapper(stream)
    assert obj.widgets["radio_1"].number_of_options == 2

    # switching the selection selects the option and clears the other one,
    # whichever of them the field lists
    for index in indices:
        obj.fill({"radio_1": index})
        result = obj.read()
        expected = [["/Off", None], ["/Off", None]]
        expected[index][0] = f"/{index}"
        assert get_widget_states(result, "radio_1") == expected
        assert find_widget(result, "radio_1")["/Parent"].get_object()["/V"] == (
            f"/{index}"
        )
        assert PdfWrapper(result).data["radio_1"] == index
        assert_widgets_match_output(obj)


@pytest.mark.parametrize("rebuild", [False, True], ids=["same", "rebuilt"])
@pytest.mark.parametrize("separate", [False, True], ids=["merged", "separate"])
def test_fill_checkbox_with_own_on_state_again(template_stream, separate, rebuild):
    # "check" is unchecked, and its on state is /Custom rather than /Yes; with
    # separate, its widget is the kid of a field whose /DV is /Off
    with Pdf.open(BytesIO(template_stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        check = get_field(pdf, "check")
        set_on_state(check)
        check.AS = Name.Off
        check.V = Name.Off
        check.Ff = 0
        if separate:
            field = pdf.make_indirect(
                Dictionary(
                    {
                        "/T": String("check"),
                        "/FT": Name.Btn,
                        "/Ff": 0,
                        "/DV": Name.Off,
                        "/Kids": Array([check]),
                    }
                )
            )
            for entry in ("/T", "/FT", "/Ff"):
                del check[entry]
            check.Parent = field
            pdf.Root.AcroForm.Fields = Array(
                [each for each in fields if each != check] + [field]
            )
        stream = save(pdf)

    obj = PdfWrapper(stream)
    obj.fill({"check": True})
    widget = find_widget(obj.read(), "check")
    assert (widget["/AS"], widget["/V"]) == ("/Custom", "/Custom")
    # it is still a checkbox when the PDF is read again
    reopened = PdfWrapper(obj.read()).widgets["check"]
    assert type(reopened) is Checkbox
    assert reopened.value is True

    # the checked state doesn't stop the checkbox from being filled again
    if rebuild:
        obj.remove_fields(["absent"])
    obj.fill({"check": False})
    widget = find_widget(obj.read(), "check")
    assert (widget["/AS"], widget["/V"]) == ("/Off", "/Off")
    assert obj.widgets["check"].value is False


@pytest.mark.parametrize("state", ["/Standby", "/Off"])
def test_pushbutton_is_not_a_checkbox(template_stream, state):
    # "check" becomes the pushbutton "action", which has appearance states but
    # no value
    with Pdf.open(BytesIO(template_stream)) as pdf:
        action = get_field(pdf, "check")
        action.T = String("action")
        action.Ff = PUSHBUTTON
        action.AP = Dictionary(
            N=Dictionary({"/Activate": action.AP.N.Yes, "/Standby": action.AP.N.Off})
        )
        action.AS = Name(state)
        for entry in ("/V", "/DV"):
            if entry in action:
                del action[entry]
        stream = save(pdf)

    obj = PdfWrapper(stream)
    assert "action" not in obj.widgets

    # filling leaves it unchanged
    widget = find_widget(obj.fill({"action": True}).read(), "action")
    assert widget["/AS"] == state
    assert "/V" not in widget


@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_unnamed_pushbutton_with_empty_parent(template_stream, use_full_widget_name):
    # "check" becomes a pushbutton without a name, whose parent is empty, so
    # its own flags decide
    with Pdf.open(BytesIO(template_stream)) as pdf:
        check = get_field(pdf, "check")
        check.Ff = PUSHBUTTON
        check.Parent = pdf.make_indirect(Dictionary())
        # replaced with null below, since pikepdf removes null entries
        check.T = String("null")
        if "/V" in check:
            del check["/V"]
        stream = save(pdf)
    writer = PdfWriter(BytesIO(stream))
    for annot in writer.pages[0]["/Annots"]:
        annot = annot.get_object()
        if annot.get("/T") == "null":
            annot[NameObject("/T")] = NullObject()
    with BytesIO() as f:
        writer.write(f)
        stream = f.getvalue()

    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert ("" if use_full_widget_name else None) not in obj.widgets

    # filling leaves it unchanged
    pushbutton = next(
        annot.get_object()
        for annot in PdfReader(BytesIO(obj.fill(obj.sample_data).read())).pages[0][
            "/Annots"
        ]
        if annot.get_object().get("/Ff") == PUSHBUTTON
    )
    assert pushbutton["/AS"] == "/Off"
    assert "/V" not in pushbutton


@pytest.mark.parametrize(
    ("states", "value", "expected"),
    [
        (["/Custom"], "/Custom", True),
        (["/A", "/B"], "/B", True),
        (["/A", "/B"], "/A", None),
        (["/A", "/B"], "/Off", None),
    ],
    ids=["one", "last", "other", "off"],
)
def test_checkbox_value_of_its_field(template_stream, states, value, expected):
    stream = checkbox_field(template_stream, states, value)

    # the field's value counts for a widget whose state it names, here the
    # last one, which "check" gives access to
    obj = PdfWrapper(stream)
    assert type(obj.widgets["check"]) is Checkbox
    assert obj.data["check"] is expected


def test_fill_keeps_checkboxes_not_supplied(template_stream, expected_pdfs):
    # "check" reads True from the field's value, which names its last widget's
    # state, while its first widget is off
    stream = checkbox_field(template_stream, ["/A", "/B"], "/B")
    obj = PdfWrapper(stream)
    assert obj.widgets["check"].value is True
    expected = [["/Off", None], ["/B", None], "/B"]

    # a value that wasn't supplied and is still the one read isn't written
    assert get_checkbox_field_states(obj.fill({}).read()) == expected
    assert get_checkbox_field_states(obj.fill({"test": "foo"}).read()) == expected

    # one that was assigned since is
    obj.widgets["check"].value = False
    assert get_checkbox_field_states(obj.fill({}).read()) == [
        ["/Off", "/Off"],
        ["/Off", "/Off"],
        "/B",
    ]

    # two checkboxes are named "c1_3[1]"; the later, checked one gives the
    # name its value, and the other stays unchecked
    path = os.path.join(
        expected_pdfs, "scenario", "test_issues", "test_use_full_widget_name_2.pdf"
    )
    with open(path, "rb") as f:
        sample = f.read()
    filled = PdfWrapper(sample).fill({}).read()
    for stream in (sample, filled):
        assert get_widget_states(stream, "c1_3[1]") == [["/Off", "/Off"], ["/5", "/5"]]


def test_fill_checkbox_back_to_value_read(template_stream):
    # "check" is checked
    with Pdf.open(BytesIO(template_stream)) as pdf:
        check = get_field(pdf, "check")
        check.AS = Name.Yes
        check.V = Name.Yes
        stream = save(pdf)

    obj = PdfWrapper(stream)
    obj.fill({"check": False})
    widget = find_widget(obj.read(), "check")
    assert (widget["/AS"], widget["/V"]) == ("/Off", "/Off")

    # the value read is assigned again after the PDF changed, so it is written
    obj.widgets["check"].value = True
    obj.fill({})
    widget = find_widget(obj.read(), "check")
    assert (widget["/AS"], widget["/V"]) == ("/Yes", "/Yes")


@pytest.mark.parametrize("radio_flag_on", ["outer", "field"])
@pytest.mark.parametrize("position", ["first", "between", "last"])
def test_radio_group_with_short_name_of_another_field(
    template_with_radiobutton_stream, radio_flag_on, position
):
    stream = name_checkbox_like_radio_group(
        template_with_radiobutton_stream, position, radio_flag_on
    )

    # the later field replaces the earlier one, as for any widget, and a radio
    # group keeps the options before the checkbox
    radio_last = position != "last"
    widget = PdfWrapper(stream).widgets["group"]
    if radio_last:
        assert isinstance(widget, Radio)
        assert widget.number_of_options == 2
    else:
        assert type(widget) is Checkbox

    # full names tell them apart
    widgets = PdfWrapper(stream, use_full_widget_name=True).widgets
    assert type(widgets["group"]) is Checkbox
    assert isinstance(widgets["outer.group"], Radio)
    assert widgets["outer.group"].number_of_options == 2

    # filling the name changes only the field it gives access to
    for value in [0, 1] if radio_last else [True]:
        filled = PdfWrapper(stream).fill({"group": value}).read()
        assert get_checkbox_and_radio_states(filled) == (
            {
                "group": ["/Off", None],
                "outer.group": [
                    "/0" if value == 0 else "/Off",
                    "/1" if value else "/Off",
                ],
                "outer.group /V": f"/{value}",
            }
            if radio_last
            else {
                "group": ["/Yes", "/Yes"],
                "outer.group": ["/Off", "/Off"],
                "outer.group /V": None,
            }
        )
        widgets = PdfWrapper(filled, use_full_widget_name=True).widgets
        assert widgets["outer.group"].value == (value if radio_last else None)
        assert widgets["group"].value is (None if radio_last else True)


@pytest.mark.parametrize(
    "checkbox_state", ["/Custom", ""], ids=["checked", "unrecognized"]
)
def test_fill_radio_group_with_other_field_of_its_name(
    template_with_radiobutton_stream, checkbox_state
):
    # the checkbox comes first, checked with its own on state, or without an
    # appearance state
    stream = name_checkbox_like_radio_group(
        template_with_radiobutton_stream, "first", checkbox_state=checkbox_state
    )
    obj = PdfWrapper(stream)
    assert obj.widgets["group"].number_of_options == 2

    # it doesn't take an option index from the radio group
    state = checkbox_state or None
    assert get_checkbox_and_radio_states(obj.fill({"group": 0}).read()) == {
        "group": [state, state],
        "outer.group": ["/0", "/Off"],
        "outer.group /V": "/0",
    }


@pytest.mark.parametrize(
    "other_state", ["/Custom", ""], ids=["checked", "unrecognized"]
)
def test_fill_checkboxes_with_one_short_name(template_stream, other_state):
    # "check_2" becomes "outer.check", which shares the short name of the
    # checkbox "check", and has its own on state; it is checked, or has no
    # appearance state, which makes it match no widget type
    with Pdf.open(BytesIO(template_stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        other = get_field(pdf, "check_2")
        other.T = String("check")
        set_on_state(other)
        for entry in ("/AS", "/V"):
            if other_state:
                other[entry] = Name(other_state)
            elif entry in other:
                del other[entry]
        outer = pdf.make_indirect(
            Dictionary({"/T": String("outer"), "/Kids": Array([other])})
        )
        other.Parent = outer
        pdf.Root.AcroForm.Fields = Array(
            [field for field in fields if field != other] + [outer]
        )
        stream = save(pdf)

    obj = PdfWrapper(stream)
    assert type(obj.widgets["check"]) is Checkbox
    filled = obj.fill({"check": False}).read()

    # filling the name changes both, as before; "outer.check" is on page 2
    assert get_widget_states(filled, "check") == [["/Off", "/Off"], ["/Off", "/Off"]]


def test_dropdown_choices_skip_text_field_with_short_name(
    sample_template_with_dropdown, assert_widgets_match_output
):
    # "test_1" becomes "billing.dropdown_1", a text field with the short name
    # of the dropdown "dropdown_1", whose widget comes later and has the key
    with Pdf.open(BytesIO(sample_template_with_dropdown)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        text = get_field(pdf, "test_1")
        text.T = String("dropdown_1")
        text.V = String("bar")
        billing = pdf.make_indirect(
            Dictionary({"/T": String("billing"), "/Kids": Array([text])})
        )
        text.Parent = billing
        pdf.Root.AcroForm.Fields = Array(
            [field for field in fields if field != text] + [billing]
        )
        stream = save(pdf)

    obj = PdfWrapper(stream)
    assert type(obj.widgets["dropdown_1"]) is Dropdown
    # "bar" is the displayed text of a new option, which the text field doesn't get
    obj.widgets["dropdown_1"].choices = ["foo", ("bar", "b")]
    output = obj.read()

    assert PdfWrapper(output, use_full_widget_name=True).data["billing.dropdown_1"] == (
        "bar"
    )
    with Pdf.open(BytesIO(output)) as pdf:
        assert "/Opt" not in get_field(pdf, "billing").Kids[0]
    assert PdfWrapper(output).widgets["dropdown_1"].choices == ("foo", ("bar", "b"))
    assert_widgets_match_output(obj)


def test_fill_checkbox_with_short_name_of_pushbutton(template_stream):
    # the widget of "test" becomes the only widget of the pushbutton
    # "outer.action", which comes before the checkbox "check", renamed "action"
    with Pdf.open(BytesIO(template_stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        widget = get_field(pdf, "test")
        check = get_field(pdf, "check")
        check.T = String("action")
        outer = pdf.make_indirect(Dictionary({"/T": String("outer")}))
        action = pdf.make_indirect(
            Dictionary(
                {
                    "/T": String("action"),
                    "/FT": Name.Btn,
                    "/Ff": PUSHBUTTON,
                    "/Kids": Array([widget]),
                    "/Parent": outer,
                }
            )
        )
        outer.Kids = Array([action])
        for entry in ("/T", "/FT", "/V", "/DA", "/Ff", "/MaxLen", "/Q"):
            if entry in widget:
                del widget[entry]
        widget.Parent = action
        widget.AP = Dictionary(
            N=Dictionary({"/Off": check.AP.N.Off, "/Activate": check.AP.N.Yes})
        )
        widget.AS = Name.Off
        pdf.Root.AcroForm.Fields = Array(
            [each for each in fields if each != widget] + [outer]
        )
        stream = save(pdf)

    obj = PdfWrapper(stream)
    assert type(obj.widgets["action"]) is Checkbox
    filled = obj.fill({"action": True}).read()

    # the pushbutton keeps having no value
    assert get_widget_states(filled, "action") == [["/Off", None], ["/Yes", "/Yes"]]


@pytest.mark.parametrize("operation", ["rebuild", "copy"])
def test_fill_checkbox_with_short_name_of_radio_group_again(
    template_with_radiobutton_stream, operation
):
    # the unchecked checkbox comes last, and the radio group's second option
    # is selected
    stream = name_checkbox_like_radio_group(
        template_with_radiobutton_stream, "last", checkbox_state="/Off", selected=1
    )
    obj = PdfWrapper(stream)
    obj.fill({"group": True})
    # the checkbox that is kept, or copied, still fills only itself
    if operation == "rebuild":
        obj.remove_fields(["absent"])
    else:
        obj = PdfArray([obj]).merge()
    assert type(obj.widgets["group"]) is Checkbox

    assert get_checkbox_and_radio_states(obj.fill({"group": False}).read()) == {
        "group": ["/Off", "/Off"],
        "outer.group": ["/Off", "/1"],
        "outer.group /V": "/1",
    }


def test_fill_checkbox_after_rename_gives_radio_group_its_name(
    template_with_radiobutton_stream,
):
    # the radio group "outer.radio" comes before the checkbox "group"
    stream = name_checkbox_like_radio_group(
        template_with_radiobutton_stream, "last", radio_name="radio"
    )
    obj = PdfWrapper(stream)
    obj.update_widget_key("radio", "group").commit_widget_key_updates()
    assert type(obj.widgets["group"]) is Checkbox

    # the checkbox kept under the name fills only itself, as after reopening
    expected = {
        "group": ["/Yes", "/Yes"],
        "outer.group": ["/Off", "/Off"],
        "outer.group /V": None,
    }
    renamed = obj.read()
    assert get_checkbox_and_radio_states(obj.fill({"group": True}).read()) == expected
    filled = PdfWrapper(renamed).fill({"group": True}).read()
    assert get_checkbox_and_radio_states(filled) == expected
