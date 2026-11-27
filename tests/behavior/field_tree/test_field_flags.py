# -*- coding: utf-8 -*-

from io import BytesIO

import pytest
from pikepdf import Array, Dictionary, Name, Pdf, String
from pypdf import PdfWriter
from pypdf.generic import NameObject, NullObject

from PyPDFForm import PdfWrapper
from PyPDFForm.lib.constants import COMB, MULTILINE, RADIO, READ_ONLY, REQUIRED
from PyPDFForm.lib.hooks import update_field_readonly
from PyPDFForm.lib.middleware.radio import Radio
from tests.support.builders import (
    OTHER_FLAG,
    get_field,
    nest_fields,
    save,
    set_parent_entry,
    with_parent_cycle,
)
from tests.support.checks import find_widget, get_nested_entries

FLAG_PROPERTIES = [
    ("readonly", READ_ONLY),
    ("required", REQUIRED),
    ("multiline", MULTILINE),
    ("comb", COMB),
]


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize(("name", "flag"), FLAG_PROPERTIES)
@pytest.mark.parametrize(
    ("holders", "is_set"),
    [
        ((), False),
        (("outer",), False),
        (("outer",), True),
        (("outer", "inner"), False),
        (("outer", "inner"), True),
        (("outer", "inner", "test"), False),
        (("outer", "inner", "test"), True),
    ],
    ids=[
        "none",
        "grandparent-unset",
        "grandparent-set",
        "parent-unset",
        "parent-set",
        "widget-unset",
        "widget-set",
    ],
)
def test_change_inherited_field_flag(
    template_stream,
    holders,
    is_set,
    name,
    flag,
    use_full_widget_name,
    assert_widgets_match_output,
):
    # each holder has flags; the lowest one has the flag set if is_set, and the
    # ones above it the other way, so the lowest one takes precedence
    flags = {
        holder: OTHER_FLAG | (flag if (holder == holders[-1]) == is_set else 0)
        for holder in holders
    }
    # "test_2" inherits from "inner" and "outer" only
    shared = is_set if holders[-1:] != ("test",) else not is_set
    stream = nest_fields(template_stream, flags, "/Ff")
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    key, other = (
        ("outer.inner.test", "outer.inner.test_2")
        if use_full_widget_name
        else ("test", "test_2")
    )
    assert getattr(obj.widgets[key], name) is is_set
    assert getattr(obj.widgets[other], name) is shared

    setattr(obj.widgets[key], name, not is_set)
    result = obj.read()

    # only the widget's own field changes, keeping the flags it inherited;
    # fields shared with "test_2" don't
    assert get_nested_entries(result, "/Ff") == {
        "test": OTHER_FLAG if is_set else flag | (OTHER_FLAG if holders else 0),
        "test_2": None,
        "inner": flags.get("inner"),
        "outer": flags.get("outer"),
        "/AcroForm": None,
    }
    reopened = PdfWrapper(result, use_full_widget_name=use_full_widget_name)
    assert getattr(reopened.widgets[key], name) is not is_set
    assert getattr(reopened.widgets[other], name) is shared
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("own", [False, True], ids=["field", "widget"])
def test_change_field_flag_of_kid_widget(
    sample_template_with_full_key, own, assert_widgets_match_output
):
    # the widget of "Date mois" has no name, so its parent is the field
    stream = set_parent_entry(
        sample_template_with_full_key,
        "Date mois",
        "/Ff",
        OTHER_FLAG if own else OTHER_FLAG | READ_ONLY,
    )
    with Pdf.open(BytesIO(stream)) as pdf:
        for page in pdf.pages:
            for annot in page.get("/Annots", []):
                if "/Parent" in annot and str(annot.Parent.get("/T")) == "Date mois":
                    if own:
                        annot.Ff = OTHER_FLAG | READ_ONLY
                    elif "/Ff" in annot:
                        del annot["/Ff"]
        stream = save(pdf)

    obj = PdfWrapper(stream)
    assert obj.widgets["Date mois"].readonly
    obj.widgets["Date mois"].readonly = False
    widget = find_widget(obj.read(), "Date mois")

    # the flags that were found change
    assert widget.get("/Ff") == (OTHER_FLAG if own else None)
    assert widget["/Parent"].get_object()["/Ff"] == OTHER_FLAG
    assert_widgets_match_output(obj)


@pytest.mark.parametrize(("name", "flag"), FLAG_PROPERTIES)
def test_change_field_flag_with_parent_cycle(
    template_stream, name, flag, assert_widgets_match_output
):
    obj = PdfWrapper(with_parent_cycle(template_stream, "test"))
    # the cycle is reached before any flags, which read as unset
    assert getattr(obj.widgets["test"], name) is False
    original = obj.read()
    # applied before the failing change, and discarded with it
    obj.widgets["test"].alignment = 2
    setattr(obj.widgets["test"], name, True)

    with pytest.raises(ValueError, match="the /Parent chain of the field has a cycle"):
        obj.read()

    assert obj.widgets["test"].alignment is None
    assert getattr(obj.widgets["test"], name) is False
    assert not obj.widgets["test"].hooks_to_trigger
    assert obj.read() == original
    assert_widgets_match_output(obj)

    # the field's own flags are found before the cycle
    with Pdf.open(BytesIO(original)) as pdf:
        get_field(pdf, "test").Ff = flag
        obj = PdfWrapper(save(pdf))
    assert getattr(obj.widgets["test"], name) is True
    setattr(obj.widgets["test"], name, False)

    assert find_widget(obj.read(), "test")["/Ff"] == 0


def test_fill_readonly_with_parent_cycle(template_stream):
    obj = PdfWrapper(with_parent_cycle(template_stream, "test"))
    original = obj.read()

    with pytest.raises(ValueError, match="the /Parent chain of the field has a cycle"):
        obj.fill({"test": "foo", "test_2": "bar"}, readonly=True)

    assert obj.read() == original
    assert obj.widgets["test"].value is None
    assert obj.widgets["test_2"].value is None
    assert obj.widgets["test_2"].readonly is False


def test_change_flag_of_widget_that_is_its_own_parent(template_stream):
    with Pdf.open(BytesIO(template_stream)) as pdf:
        field = get_field(pdf, "test")
        field.Parent = field
        stream = save(pdf)

    # the cycle is reached before any flags, which read as unset
    obj = PdfWrapper(stream)
    original = obj.read()
    assert obj.widgets["test"].readonly is False
    obj.widgets["test"].readonly = True

    with pytest.raises(ValueError, match="the /Parent chain of the field has a cycle"):
        obj.read()
    assert obj.widgets["test"].readonly is False
    assert obj.read() == original


@pytest.mark.parametrize("holder", ["test", "outer"])
@pytest.mark.parametrize(
    "value",
    [String(""), Array([]), Dictionary({}), True],
    ids=["string", "array", "dictionary", "boolean"],
)
def test_reject_field_flags_that_are_not_a_number(template_stream, value, holder):
    # on the field, or on a field above its parent
    stream = nest_fields(template_stream, {holder: value}, "/Ff")
    message = "Cannot read the field flags: /Ff .* is not a number"

    # they aren't read as no flags
    with pytest.raises(ValueError, match=message):
        PdfWrapper(stream)

    # nor overwritten by a change
    widget = find_widget(stream, "test")
    chain = [widget, widget["/Parent"], widget["/Parent"]["/Parent"]]
    before = [repr(each.get("/Ff")) for each in chain]
    with pytest.raises(ValueError, match=message):
        update_field_readonly(widget, True)
    assert [repr(each.get("/Ff")) for each in chain] == before


def test_change_null_field_flags(template_stream, assert_widgets_match_output):
    writer = PdfWriter(BytesIO(template_stream))
    for annot in writer.pages[0]["/Annots"]:
        annot = annot.get_object()
        if annot.get("/T") == "test":
            annot[NameObject("/Ff")] = NullObject()
    with BytesIO() as f:
        writer.write(f)
        stream = f.getvalue()

    # a null /Ff is absent, so the field has no flags
    obj = PdfWrapper(stream)
    assert obj.widgets["test"].readonly is False
    obj.widgets["test"].readonly = True

    assert find_widget(obj.read(), "test")["/Ff"] == READ_ONLY
    assert_widgets_match_output(obj)


@pytest.mark.parametrize(
    ("name", "flag"), [("readonly", READ_ONLY), ("required", REQUIRED)]
)
@pytest.mark.parametrize("selected", [None, 0, 1])
def test_change_flag_of_radio_group_with_inherited_radio_flag(
    template_with_radiobutton_stream, name, flag, selected, assert_widgets_match_output
):
    # "radio_1" is a kid of "outer", which sets its radio flag, and its /DV is
    # /Off, as a checkbox's can be
    with Pdf.open(BytesIO(template_with_radiobutton_stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        radio = get_field(pdf, "radio_1")
        outer = pdf.make_indirect(
            Dictionary({"/T": String("outer"), "/Kids": Array([radio]), "/Ff": RADIO})
        )
        radio.Parent = outer
        del radio["/Ff"]
        radio.DV = Name.Off
        if selected is not None:
            radio.V = Name(f"/{selected}")
            radio.Kids[selected].AS = Name(f"/{selected}")
        pdf.Root.AcroForm.Fields = Array(
            [field for field in fields if field != radio] + [outer]
        )
        stream = save(pdf)

    obj = PdfWrapper(stream)
    assert isinstance(obj.widgets["radio_1"], Radio)
    assert obj.widgets["radio_1"].value == selected
    setattr(obj.widgets["radio_1"], name, True)
    result = obj.read()

    # the flag change keeps the widget a radio group with the same value
    reopened = PdfWrapper(result).widgets["radio_1"]
    assert isinstance(reopened, Radio)
    assert reopened.value == selected
    assert getattr(reopened, name) is True
    # the inherited radio flag is copied to the field's own flags
    field = find_widget(result, "radio_1")["/Parent"].get_object()
    assert field["/Ff"] == RADIO | flag
    assert field["/Parent"].get_object()["/Ff"] == RADIO
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("local", [0, 1], ids=["first", "last"])
def test_radio_option_with_own_field_flags(
    template_with_radiobutton_stream, local, assert_widgets_match_output
):
    # one option of "radio_1" has flags of its own, without the radio flag that
    # its field sets, and the field's /DV is /Off, as a checkbox's can be
    with Pdf.open(BytesIO(template_with_radiobutton_stream)) as pdf:
        radio = get_field(pdf, "radio_1")
        radio.DV = Name.Off
        radio.Kids[local].Ff = READ_ONLY
        stream = save(pdf)

    # every option is classified by its field's flags, whichever comes first
    obj = PdfWrapper(stream)
    assert isinstance(obj.widgets["radio_1"], Radio)
    assert obj.widgets["radio_1"].number_of_options == 2

    obj.widgets["radio_1"].required = True
    reopened = PdfWrapper(obj.read()).widgets["radio_1"]
    assert isinstance(reopened, Radio)
    assert reopened.number_of_options == 2
    assert_widgets_match_output(obj)
