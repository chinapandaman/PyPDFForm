# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from pikepdf import Pdf, String

from PyPDFForm import BlankPage, Fields, PdfWrapper
from PyPDFForm.lib.middleware.checkbox import Checkbox
from tests.support.builders import change_widgets, get_field, save, split_widgets
from tests.support.checks import find_widget, get_normal_appearance


@pytest.mark.parametrize("field_name", ["test", "check", "radio_1"])
def test_scalar_geometry(template_stream, template_with_radiobutton_stream, field_name):
    template = (
        template_with_radiobutton_stream if field_name == "radio_1" else template_stream
    )
    attributes = {"x": 123, "y": 0, "width": 80, "height": 40}
    form = PdfWrapper(template)
    float_form = PdfWrapper(template)
    expected = {name: getattr(form.widgets[field_name], name) for name in attributes}
    updates = attributes.copy()
    if field_name != "test":
        updates["size"] = 30

    for attribute, value in updates.items():
        setattr(form.widgets[field_name], attribute, value)
        setattr(float_form.widgets[field_name], attribute, float(value))
        for name in ("width", "height") if attribute == "size" else (attribute,):
            original = expected[name]
            expected[name] = (
                [value] * len(original) if isinstance(original, list) else value
            )

        stream = form.read()
        assert stream == float_form.read()
        reopened = PdfWrapper(stream)
        for name, expected_value in expected.items():
            for widget in (form.widgets[field_name], reopened.widgets[field_name]):
                assert getattr(widget, name) == pytest.approx(expected_value)


def test_invalid_scalar_geometry(template_stream):
    form = PdfWrapper(template_stream)
    expected = form.read()
    widget = form.widgets["check"]
    state = dict(vars(widget))

    for attribute in ("x", "y", "width", "height", "size"):
        for value in ("123", True, [123]):
            with pytest.raises(
                TypeError, match="Geometry values must be integers or floats"
            ):
                setattr(widget, attribute, value)

        with pytest.raises(TypeError, match=f"property '{attribute}' cannot be None"):
            setattr(widget, attribute, None)

    # rejected before the widget changes, so reads don't retry them
    assert vars(widget) == state
    assert not widget.hooks_to_trigger
    assert form.read() == expected


@pytest.mark.parametrize(
    ("template", "key", "supported"),
    [
        (
            "sample_template_with_radio_button.pdf",
            "test",
            [
                "font",
                "font_size",
                "font_color",
                "comb",
                "alignment",
                "multiline",
                "max_length",
            ],
        ),
        ("sample_template_with_radio_button.pdf", "check", ["size"]),
        ("sample_template_with_radio_button.pdf", "radio_1", ["size"]),
        (
            os.path.join("dropdown", "sample_template_with_dropdown.pdf"),
            "dropdown_1",
            ["font", "font_size", "font_color", "choices"],
        ),
        ("sample_template_with_full_key.pdf", "Signature17", []),
        ("sample_template_with_image_field.pdf", "image_1", []),
    ],
)
def test_set_unsupported_widget_property(pdf_samples, template, key, supported):
    type_specific_properties = [
        "font",
        "font_size",
        "font_color",
        "comb",
        "alignment",
        "multiline",
        "max_length",
        "choices",
        "size",
    ]
    unsupported = [each for each in type_specific_properties if each not in supported]
    obj = PdfWrapper(os.path.join(pdf_samples, template))
    expected = obj.read()
    widget = obj.widgets[key]
    state = dict(vars(widget))

    for name in unsupported:
        for value in (1, None):
            with pytest.raises(
                AttributeError,
                match=rf"^{type(widget).__name__} field '{key}' does not support "
                rf"property '{name}'\.$",
            ):
                setattr(widget, name, value)

        assert not hasattr(widget, name)

    assert not widget.hooks_to_trigger
    assert vars(widget) == state
    assert obj.read() == expected


def test_clear_text_field_properties(template_stream, assert_widgets_match_output):
    obj = PdfWrapper(template_stream)
    widget = obj.widgets["test"]
    widget.multiline = True
    widget.comb = True
    widget.tooltip = "tooltip"
    widget.max_length = 4
    widget.alignment = 2
    assert_widgets_match_output(obj)

    widget.multiline = False
    widget.comb = False
    widget.tooltip = ""
    widget.max_length = None
    widget.alignment = None
    assert widget.tooltip is None
    assert_widgets_match_output(obj)

    reopened = PdfWrapper(obj.read()).widgets["test"]
    assert reopened.multiline is False
    assert reopened.comb is False
    assert reopened.tooltip is None
    assert reopened.max_length is None
    assert reopened.alignment is None


def test_read_style_of_created_fields(template_stream, assert_widgets_match_output):
    obj = PdfWrapper(template_stream).bulk_create_fields(
        [
            Fields.TextField(
                name="new_text",
                page_number=1,
                x=100,
                y=100,
                font="Helvetica",
                font_size=20,
                font_color=(0, 0, 1),
            ),
            Fields.DropdownField(
                name="new_dropdown",
                page_number=1,
                x=300,
                y=100,
                options=["a", "b"],
                font_size=15,
                font_color=(1, 0, 0),
            ),
        ]
    )
    obj.read()

    text = obj.widgets["new_text"]
    dropdown = obj.widgets["new_dropdown"]
    assert (text.font, text.font_size, text.font_color) == ("/Helv", 20, (0, 0, 1))
    assert (dropdown.font_size, dropdown.font_color) == (15, (1, 0, 0))
    assert_widgets_match_output(obj)


@pytest.mark.parametrize(
    ("attribute", "value", "removed"),
    [
        ("font", "registered", True),
        ("font_size", 20, True),
        ("font_color", (1, 0, 0), True),
        ("alignment", 1, True),
        ("multiline", True, True),
        ("comb", True, True),
        ("max_length", 5, True),
        ("width", 100, True),
        ("height", 30, True),
        ("x", 50, False),
        ("y", 50, False),
        ("tooltip", "tooltip", False),
        ("readonly", True, False),
        ("required", True, False),
        ("hidden", True, False),
    ],
)
def test_restyle_removes_stale_appearance(
    pdf_samples,
    sample_font_stream,
    attribute,
    value,
    removed,
    assert_valid_appearances,
):
    form = PdfWrapper(os.path.join(pdf_samples, "sample_template_filled.pdf"))
    form.register_font("registered", sample_font_stream)
    original = form.read()

    setattr(form.widgets["test"], attribute, value)
    output = form.read()

    assert_valid_appearances(output)
    assert ("/AP" not in find_widget(output, "test")) is removed
    # the other fields keep theirs
    assert get_normal_appearance(output, "test_2") == get_normal_appearance(
        original, "test_2"
    )


def test_change_choices_removes_stale_appearance(sample_template_with_dropdown):
    form = PdfWrapper(sample_template_with_dropdown)
    form.widgets["dropdown_1"].choices = ["a", "b"]

    assert "/AP" not in find_widget(form.read(), "dropdown_1")


def test_cleared_selection_removes_appearance():
    # a created dropdown keeps the appearance that draws its selection, Apple
    form = PdfWrapper(
        PdfWrapper(BlankPage())
        .bulk_create_fields(
            [Fields.DropdownField("choice", 1, 20, 20, options=["Apple", "Banana"])]
        )
        .read()
    )
    assert "/AP" in find_widget(form.read(), "choice")

    # the choices end as they started, but the selection is cleared
    form.widgets["choice"].choices = ["Pear"]
    form.widgets["choice"].choices = ["Apple", "Banana"]
    output = form.read()
    annot = find_widget(output, "choice")
    assert form.data["choice"] is PdfWrapper(output).data["choice"] is None
    assert "/V" not in annot
    assert "/AP" not in annot


@pytest.mark.parametrize(
    ("indices", "expected"), [([2], [1]), (None, None)], ids=["stale", "missing"]
)
def test_change_choices_rewrites_stale_index(
    sample_template_with_dropdown, indices, expected, assert_widgets_match_output
):
    # "bar" is selected at index 1, and /I points at index 2 or is missing
    stream = change_widgets(
        PdfWrapper(sample_template_with_dropdown).fill({"dropdown_1": 1}).read(),
        {
            "dropdown_1": lambda annot: (
                setattr(annot, "I", indices) if indices else annot.__delitem__("/I")
            )
        },
    )
    form = PdfWrapper(stream)
    assert form.data["dropdown_1"] == 1

    # "bar" stays at index 1, so a stale /I is rewritten and a missing one isn't added
    form.widgets["dropdown_1"].choices = ["foobar", "bar", "foo"]
    output = form.read()
    annot = find_widget(output, "dropdown_1")
    assert form.data["dropdown_1"] == PdfWrapper(output).data["dropdown_1"] == 1
    assert annot["/V"] == "bar"
    assert annot.get("/I") == expected
    assert_widgets_match_output(form)


def test_resize_keeps_checkbox_appearance(template_stream, assert_valid_appearances):
    form = PdfWrapper(template_stream)
    form.widgets["check"].width = 30
    output = form.read()

    # it holds the checkbox's states
    assert_valid_appearances(output)
    assert "/AP" in find_widget(output, "check")


@pytest.mark.parametrize(
    "attribute",
    [
        "font",
        "font_size",
        "font_color",
        "alignment",
        "multiline",
        "comb",
        "max_length",
        "width",
        "height",
    ],
)
def test_restyle_to_same_value_keeps_appearance(pdf_samples, attribute):
    form = PdfWrapper(os.path.join(pdf_samples, "sample_template_filled.pdf"))
    widget = form.widgets["test"]
    setattr(widget, attribute, getattr(widget, attribute))

    # what the appearance draws didn't change
    assert widget.hooks_to_trigger
    assert "/AP" in find_widget(form.read(), "test")


@pytest.mark.parametrize(("attribute", "value"), [("alignment", 2), ("font_size", 20)])
def test_restyle_shared_field_removes_every_appearance(pdf_samples, attribute, value):
    with Pdf.open(os.path.join(pdf_samples, "sample_template_filled.pdf")) as pdf:
        field = get_field(pdf, "test")
        widgets = split_widgets(pdf, field, 2)
        field.Q = 0
        assert all("/AP" in each for each in widgets)
        template = save(pdf)
    form = PdfWrapper(template)

    # the first widget's hooks change /Q or /DA of the field both widgets share
    setattr(form.widgets["test"], attribute, value)

    with Pdf.open(BytesIO(form.read())) as pdf:
        assert all("/AP" not in each for each in get_field(pdf, "test").Kids)


@pytest.mark.parametrize(
    ("attribute", "value", "decorated"),
    [
        (None, None, True),
        ("font_size", 20, True),
        ("width", 120, True),
        ("width", 200, False),
    ],
)
def test_restyle_with_generated_appearances(
    template_stream, attribute, value, decorated, assert_valid_appearances
):
    form = PdfWrapper(template_stream, generate_appearance_streams=True)
    form.bulk_create_fields(
        [
            Fields.TextField(
                name="new",
                page_number=1,
                x=100,
                y=300,
                width=120,
                height=30,
                bg_color=(0.8, 0.9, 1),
            )
        ]
    )

    if attribute is not None:
        setattr(form.widgets["new"], attribute, value)
    output = form.fill({"new": "value"}).read()

    # the generator draws in the appearance, keeping its background, unless
    # the widget's size changed
    assert_valid_appearances(output)
    appearance = get_normal_appearance(output, "new")
    assert b"(value) Tj" in appearance
    assert (b".8 .9 1 rg" in appearance) is decorated
    widget = find_widget(output, "new")
    bbox, rect = widget["/AP"]["/N"]["/BBox"], widget["/Rect"]
    assert bbox[2] - bbox[0] == rect[2] - rect[0]


@pytest.mark.parametrize(
    ("index", "kept", "renamed"),
    [(0, (20, "pending"), (10, "first")), (1, (10, "first"), (20, "pending"))],
    ids=["first", "last"],
)
def test_rename_by_index(
    template_stream, index, kept, renamed, assert_widgets_match_output
):
    # two text fields named "test", with their own style, alignment, and value
    with Pdf.open(BytesIO(template_stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        first = next(field for field in fields if str(field.get("/T")) == "test")
        second = next(field for field in fields if str(field.get("/T")) == "test_2")
        first.DA = String("/Helv 10 Tf 0 g")
        first.Q = 0
        first.V = String("first")
        second.T = String("test")
        second.DA = String("/Cour 20 Tf 1 0 0 rg")
        second.Q = 2
        second.V = String("second")
        stream = save(pdf)

    obj = PdfWrapper(stream)
    # the key gives access to the last field, whose value isn't filled yet
    obj.widgets["test"].value = "pending"
    obj.update_widget_key("test", "renamed", index)
    obj.commit_widget_key_updates()

    # each key reads its field, and the value stays with the field it was set on
    for key, (font_size, value) in (("test", kept), ("renamed", renamed)):
        assert obj.widgets[key].font_size == font_size
        assert obj.widgets[key].value == value
    obj.fill({})
    assert_widgets_match_output(obj)


@pytest.mark.parametrize(
    ("index", "kept", "renamed"),
    [
        (0, (("x", "y", "z"), 2), (("a", "b"), 0)),
        (1, (("a", "b"), 0), (("x", "y", "z"), 2)),
    ],
    ids=["first", "last"],
)
def test_rename_dropdown_by_index(
    template_stream, index, kept, renamed, assert_widgets_match_output
):
    # two dropdowns named "dropdown", with two and three choices
    stream = (
        PdfWrapper(template_stream)
        .bulk_create_fields(
            [
                Fields.DropdownField(
                    name="dropdown", page_number=1, x=100, y=100, options=["a", "b"]
                ),
                Fields.DropdownField(
                    name="other", page_number=1, x=300, y=100, options=["x", "y", "z"]
                ),
            ]
        )
        .read()
    )
    with Pdf.open(BytesIO(stream)) as pdf:
        for field in pdf.Root.AcroForm.Fields:
            if str(field.get("/T")) == "other":
                field.T = String("dropdown")
        stream = save(pdf)

    obj = PdfWrapper(stream)
    # the key gives access to the last dropdown, whose selection isn't filled yet
    obj.widgets["dropdown"].value = 2
    obj.update_widget_key("dropdown", "renamed", index)
    obj.commit_widget_key_updates()

    # the choices and the selection are those of one field
    for key, (choices, value) in (("dropdown", kept), ("renamed", renamed)):
        assert (obj.widgets[key].choices, obj.widgets[key].value) == (choices, value)
    obj.fill({"test": "foo"})
    assert_widgets_match_output(obj)


def test_create_field_beside_field_without_name(template_stream):
    # without full names, "test", which has no name, is keyed None
    with Pdf.open(BytesIO(template_stream)) as pdf:
        for field in pdf.Root.AcroForm.Fields:
            if str(field.get("/T")) == "test":
                del field["/T"]
        stream = save(pdf)

    obj = PdfWrapper(stream)
    obj.widgets[None].value = "pending"
    obj.bulk_create_fields([Fields.TextField(name="new", page_number=1, x=100, y=100)])

    # the created field doesn't take the state of the field without a name
    assert obj.widgets[None].value == "pending"
    assert obj.widgets["new"].value == PdfWrapper(obj.read()).widgets["new"].value


def test_rename_to_key_of_field_of_another_type(
    template_stream, assert_widgets_match_output
):
    obj = PdfWrapper(template_stream)
    obj.widgets["check"].value = True
    obj.update_widget_key("check", "test").commit_widget_key_updates()

    # the key gives access to the checkbox, which comes after the text field,
    # as after reopening, and its value not filled yet stays with it
    assert type(obj.widgets["test"]) is Checkbox
    assert obj.widgets["test"].value is True
    obj.fill({})
    assert_widgets_match_output(obj)


def test_commit_widget_key_updates_without_pdf():
    # a wrapper without a PDF has no fields to rename
    obj = PdfWrapper().update_widget_key("a", "b").commit_widget_key_updates()

    assert obj.widgets == {}
