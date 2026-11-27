# -*- coding: utf-8 -*-

import os
from copy import deepcopy
from io import BytesIO
from unittest.mock import patch

import pytest
from jsonschema import ValidationError, validate
from pikepdf import Name, Pdf
from PIL import UnidentifiedImageError
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from PyPDFForm import BlankPage, Fields, PdfWrapper
from PyPDFForm.lib.patterns import get_widget_key
from tests.support.checks import assert_annotation_graph, page_contents


@pytest.mark.parametrize(
    ("filename", "name", "spanning_pages"),
    [
        ("sample_template_with_radio_button.pdf", "radio_1", True),
        ("sample_template_sejda.pdf", "purchase_option", False),
    ],
)
def test_radio_group_selection(
    pdf_samples, filename, name, spanning_pages, assert_round_trip
):
    with Pdf.open(os.path.join(pdf_samples, filename)) as pdf:
        group = next(field for field in pdf.Root.AcroForm.Fields if name == field.T)
        children = list(group.Kids)
        if spanning_pages:
            # Reverse page traversal order without changing /Kids or /Opt order.
            moved = children.pop(0)
            pdf.pages[0].Annots = [
                annot for annot in pdf.pages[0].Annots if annot.objgen != moved.objgen
            ]
            pdf.pages[1].Annots.append(moved)
            moved.P = pdf.pages[1].obj
            children.append(moved)
        states = [
            next(key for key in child.AP.N if key != "/Off") for child in children
        ]
        exports = [str(value) for value in group.get("/Opt", [])]
        # Start with an existing selection, independently of PdfWrapper.fill.
        group.V = Name(states[0])
        for index, child in enumerate(children):
            child.AS = Name(states[0] if index == 0 else "/Off")
        stream = BytesIO()
        pdf.save(stream)

    form = PdfWrapper(stream.getvalue())
    assert form.widgets[name].value == 0
    for reopen in (False, True):
        for index in (1, 0):
            form.fill({name: index})
            result = form.read()
            with Pdf.open(BytesIO(result)) as pdf:
                group = next(
                    field for field in pdf.Root.AcroForm.Fields if name == field.T
                )
                assert states[index] == group.V
                assert [str(child.AS) for child in group.Kids] == [
                    states[index] if states[index] in child.AP.N else "/Off"
                    for child in group.Kids
                ]
                assert [str(value) for value in group.get("/Opt", [])] == exports
            assert_round_trip(form, {name: index})
            if reopen:
                form = PdfWrapper(result)


def test_choice_indices(sample_template_with_dropdown, assert_round_trip):
    for field_name, count in (("dropdown_1", 4), ("radio_1", 3)):
        for index in (0, count - 1):
            form = PdfWrapper(sample_template_with_dropdown)
            widget = form.widgets[field_name]
            validate({field_name: index}, form.schema)
            with patch.object(
                widget,
                "validate_choice_index",
                wraps=widget.validate_choice_index,
            ) as validation:
                form.fill({field_name: index})
                assert validation.call_count == 1
                validation.reset_mock()
                widget.value = index
                assert validation.call_count == 1

            assert form.widgets[field_name] is widget
            assert_round_trip(form, {field_name: index})
            annotations = [
                reference.get_object()
                for page in PdfReader(BytesIO(form.read())).pages
                for reference in page.get("/Annots", [])
                if get_widget_key(reference.get_object(), False) == field_name
            ]
            assert annotations
            if field_name == "dropdown_1":
                choices = form.widgets[field_name].choices
                assert choices is not None
                assert annotations[0]["/V"] == choices[index]
                assert annotations[0]["/I"] == [index]
            else:
                assert len(annotations) == count
                selected = annotations[index]
                assert selected["/AS"] != "/Off"
                assert selected["/Parent"]["/V"] == selected["/AS"]
                assert all(
                    annotation["/AS"] == "/Off"
                    for i, annotation in enumerate(annotations)
                    if i != index
                )

    form = PdfWrapper(sample_template_with_dropdown)
    widget = form.widgets["dropdown_1"]
    widget.choices = []
    widget.value = None
    validate({"dropdown_1": "new option"}, form.schema)
    form.fill({"dropdown_1": "new option"})
    assert widget.choices == ["new option"]
    assert widget.value == 0


@pytest.mark.parametrize(("field_name", "count"), [("dropdown_1", 4), ("radio_1", 3)])
@pytest.mark.parametrize("empty", [False, True])
def test_invalid_choice_indices(
    sample_template_with_dropdown, field_name, count, empty
):
    option_count = 0 if empty else count
    form = PdfWrapper(sample_template_with_dropdown).fill({field_name: count - 1})
    widget = form.widgets[field_name]
    if empty:
        if field_name == "dropdown_1":
            widget.choices = []
        else:
            widget.number_of_options = 0
        widget.value = None
    stream = form.read()
    original_state = deepcopy(
        {key: value.__dict__ for key, value in form.widgets.items()}
    )
    for index in (-999, -1, option_count, option_count + 999):
        with pytest.raises(ValidationError):
            validate({field_name: index}, form.schema)
        with pytest.raises(ValueError, match="Choice index"):
            widget.value = index
        with pytest.raises(ValueError, match="Choice index"):
            form.fill(
                {
                    "test_1": "must not change",
                    "dropdown_1": "must not append",
                    field_name: index,
                },
                readonly=True,
            )

        assert {
            key: value.__dict__ for key, value in form.widgets.items()
        } == original_state
        assert form.read() == stream


@pytest.mark.parametrize(("field_name", "count"), [("dropdown_1", 4), ("radio_1", 3)])
@pytest.mark.parametrize("option_count", [1, 0])
def test_stale_choice_indices(
    sample_template_with_dropdown, field_name, count, option_count
):
    form = PdfWrapper(sample_template_with_dropdown).fill(
        {field_name: count - 1, "test_1": "original"}
    )
    widget = form.widgets[field_name]
    if field_name == "dropdown_1":
        choices = widget.choices
        assert choices is not None
        widget.choices = choices[:option_count]
    else:
        widget.number_of_options = option_count
    form.widgets["test_1"].x = 123
    stream = getattr(form, "_stream")
    original_state = deepcopy(
        {key: value.__dict__ for key, value in form.widgets.items()}
    )

    with pytest.raises(ValidationError):
        validate({field_name: widget.value}, form.schema)
    with pytest.raises(ValueError, match="Choice index"):
        form.fill({"test_1": "must not change"}, readonly=True)

    assert {
        key: value.__dict__ for key, value in form.widgets.items()
    } == original_state
    assert getattr(form, "_stream") == stream
    form.fill({field_name: 0 if option_count else None})
    assert widget.value == (0 if option_count else None)


def test_dropdown_display_and_export_values(assert_round_trip):
    def get_field(output):
        return PdfReader(BytesIO(output)).pages[0]["/Annots"][0].get_object()

    form = PdfWrapper(BlankPage()).bulk_create_fields(
        [Fields.DropdownField("choice", 1, 20, 20, options=["Apple", "Banana"])]
    )
    widget = form.widgets["choice"]
    widget.choices = [("Pear", "P"), ("Grape", "G"), ("Grape", "R")]
    opt = [["P", "Pear"], ["G", "Grape"], ["R", "Grape"]]

    # by index, displayed text, and export value
    for selection, index in ((1, 1), ("Pear", 0), ("G", 1), ("R", 2)):
        output = form.fill({"choice": selection}).read()
        field = get_field(output)
        assert [list(each) for each in field["/Opt"]] == opt
        assert field["/V"] == opt[index][0]
        assert field["/I"] == [index]
        assert_round_trip(form, {"choice": index})
        assert PdfWrapper(output).widgets["choice"].choices == (
            ("Pear", "P"),
            ("Grape", "G"),
            ("Grape", "R"),
        )

    # displayed text shared by options with different export values
    stream = form.read()
    with pytest.raises(ValidationError):
        validate({"choice": "Grape"}, form.schema)
    with pytest.raises(ValueError, match="use an option index"):
        form.fill({"choice": "Grape"})
    assert widget.value == 2
    assert form.read() == stream

    # a new value is appended without dropping export values
    output = PdfWrapper(stream).fill({"choice": "Cherry"}).read()
    field = get_field(output)
    assert [list(each) for each in field["/Opt"]] == opt + [["Cherry", "Cherry"]]
    assert field["/V"] == "Cherry"
    assert PdfWrapper(output).data == {"choice": 3}

    # indirect /V, /I, and /I element choose among options sharing an export value
    widget.choices = [("Apple", "X"), ("X", "X")]
    writer = PdfWriter(clone_from=PdfReader(BytesIO(form.fill({"choice": 1}).read())))
    add_object = writer._add_object  # type: ignore # noqa: SLF001
    field = writer.pages[0]["/Annots"][0].get_object()
    field[NameObject("/V")] = add_object(TextStringObject("X"))
    field[NameObject("/I")] = add_object(ArrayObject([add_object(NumberObject(1))]))
    stream = BytesIO()
    writer.write(stream)
    reopened = PdfWrapper(stream.getvalue())
    assert reopened.data == {"choice": 1}
    assert get_field(reopened.fill({}).read())["/I"] == [1]


def test_schema(sample_template_with_dropdown):
    obj = PdfWrapper(sample_template_with_dropdown)

    for key, value in obj.schema["properties"].items():
        if key == "dropdown_1":
            for each in value["anyOf"]:
                if each["type"] == "integer":
                    assert each["maximum"] == 3

    assert obj.sample_data["dropdown_1"] == 3


def test_dropdown_not_specified(sample_template_with_dropdown):
    assert (
        PdfWrapper(sample_template_with_dropdown)
        .fill(
            {
                "test_1": "test_1",
                "test_2": "test_2",
                "test_3": "test_3",
                "check_1": True,
                "check_2": True,
                "check_3": True,
                "radio_1": 1,
            }
        )
        .read()
    )


def test_failed_fill_restores_dropdown(
    sample_template_with_dropdown, assert_widgets_match_output
):
    obj = PdfWrapper(sample_template_with_dropdown)
    original = obj.read()
    data = obj.data
    choices = obj.widgets["dropdown_1"].choices

    with (
        patch("PyPDFForm.lib.wrapper.fill", side_effect=RuntimeError),
        pytest.raises(RuntimeError),
    ):
        obj.fill({"test_1": "test_1", "dropdown_1": "new choice"})

    assert obj.data == data
    assert obj.widgets["dropdown_1"].choices == choices
    assert not any(widget.hooks_to_trigger for widget in obj.widgets.values())
    assert obj.read() == original
    assert_widgets_match_output(obj)


def test_fill_preserves_unrelated_annotations(
    annotated_form, image_samples, assert_catalog_fields, assert_annotations_preserved
):
    form = annotated_form
    full_names = form.use_full_widget_name
    key = "group.first" if full_names else "first"
    text_key = "group.text" if full_names else "text"
    original_widgets = form.widgets.copy()
    expected_keys = set(original_widgets) - {key}
    image = os.path.join(image_samples, "sample_signature.png")
    original = form.read()

    assert form.fill({key: image}) is form

    assert set(form.widgets) == expected_keys
    assert (
        set(form.data)
        == set(form.schema["properties"])
        == set(form.sample_data)
        == expected_keys
    )
    assert all(form.widgets[name] is original_widgets[name] for name in expected_keys)
    assert form.widgets[text_key].value == "retained value"
    stream = form.read()
    assert_annotation_graph(stream, expected_keys, full_names, assert_catalog_fields)
    # Filling also rewrites the text field that keeps its value.
    assert_annotations_preserved(original, stream, changed={key, text_key})
    reader = PdfReader(BytesIO(stream))
    assert len(reader.pages[0].images) == 1
    assert not reader.pages[1].images
    contents = reader.pages[0].get_contents()
    assert contents is not None
    content = contents.get_data()
    assert b" Do" in content

    # Later ordinary fills must neither redraw the consumed image nor discard styles.
    form.widgets[text_key].tooltip = "retained style"
    form.fill({text_key: "later value"})
    reopened = PdfWrapper(form.read(), use_full_widget_name=full_names)
    assert reopened.widgets[text_key].value == "later value"
    assert reopened.widgets[text_key].tooltip == "retained style"
    contents = PdfReader(BytesIO(form.read())).pages[0].get_contents()
    assert contents is not None
    assert contents.get_data() == content
    stream = form.read()
    assert_annotation_graph(stream, expected_keys, full_names, assert_catalog_fields)

    image_key = "group.image" if full_names else "image"
    form.fill({image_key: image})
    expected_keys.remove(image_key)
    assert set(form.widgets) == expected_keys
    assert_annotation_graph(
        form.read(), expected_keys, full_names, assert_catalog_fields
    )
    assert_annotations_preserved(stream, form.read(), changed={image_key})
    contents = PdfReader(BytesIO(form.read())).pages[0].get_contents()
    assert contents is not None
    assert contents.get_data().count(b" Do") == 2


@pytest.mark.parametrize("annotated_form", [True], indirect=True, ids=["full-names"])
@pytest.mark.parametrize(
    ("image", "error"),
    [
        (b"invalid image", UnidentifiedImageError),
        ("missing_image.png", FileNotFoundError),
    ],
)
def test_failed_image_fill_preserves_annotations(
    annotated_form,
    image_samples,
    image,
    error,
    assert_catalog_fields,
    assert_widgets_match_output,
):
    form = annotated_form
    original = form.read()
    original_widgets = form.widgets.copy()
    original_data = form.data

    with pytest.raises(error):
        form.fill(
            {
                "group.first": os.path.join(image_samples, "sample_signature.png"),
                "group.image": image
                if isinstance(image, bytes)
                else os.path.join(image_samples, image),
            }
        )

    assert form.widgets == original_widgets
    # the valid signature filled before the failure is not kept either
    assert form.data == original_data
    assert form.read() == original
    assert_widgets_match_output(form)
    assert_annotation_graph(
        form.read(),
        set(original_widgets),
        form.use_full_widget_name,
        assert_catalog_fields,
    )


def test_fill_removes_empty_signature_field_tree(image_samples, assert_catalog_fields):
    writer = PdfWriter()
    writer.add_blank_page(612, 792)
    annotation = writer.add_annotation(
        0,
        {
            "/Subtype": "/Widget",
            "/FT": "/Sig",
            "/Rect": [40, 100, 200, 150],
        },
    )
    root = annotation.indirect_reference
    assert root is not None
    # A separate named field owns an unnamed widget, under an emptyable group.
    for name in ("signature", "group"):
        parent = writer._add_object(  # type: ignore # noqa: SLF001
            DictionaryObject(
                {
                    NameObject("/T"): TextStringObject(name),
                    NameObject("/Kids"): ArrayObject([root]),
                }
            )
        )
        child = root.get_object()
        assert isinstance(child, DictionaryObject)
        child[NameObject("/Parent")] = parent
        root = parent
    writer.root_object[NameObject("/AcroForm")] = DictionaryObject(
        {NameObject("/Fields"): ArrayObject([root])}
    )
    stream = BytesIO()
    writer.write(stream)
    form = PdfWrapper(stream.getvalue(), use_full_widget_name=True)
    form.fill({"group.signature": os.path.join(image_samples, "sample_signature.png")})

    assert form.widgets == {}
    reader = PdfReader(BytesIO(form.read()))
    assert not reader.pages[0]["/Annots"]
    assert_catalog_fields(form.read(), [])
    assert PdfWrapper(form.read()).widgets == {}
    assert len(reader.pages[0].images) == 1


def test_signature_schema(pdf_samples):
    obj = PdfWrapper(
        os.path.join(pdf_samples, "signature", "sample_template_with_signature.pdf")
    )

    assert obj.widgets["signature"].schema_definition == {"type": "string"}


def test_signature_sample_value(pdf_samples):
    obj = PdfWrapper(
        os.path.join(pdf_samples, "signature", "sample_template_with_signature.pdf")
    )

    assert obj.widgets["signature"].sample_value == os.path.expanduser(
        "~/Downloads/sample_image.jpg"
    )


@pytest.mark.parametrize(
    ("template", "key", "preserve"),
    [
        (
            os.path.join("signature", "sample_template_with_signature_overlap.pdf"),
            "signature",
            False,
        ),
        ("sample_template_with_image_field.pdf", "image_1", True),
    ],
)
def test_rename_keeps_preserve_aspect_ratio(
    pdf_samples, image_samples, template, key, preserve
):
    path = os.path.join(pdf_samples, template)
    image = os.path.join(image_samples, "sample_image.jpg")
    renamed, same, different = (PdfWrapper(path) for _ in range(3))
    # preserve differs from the field's default
    for form, setting in (
        (renamed, preserve),
        (same, preserve),
        (different, not preserve),
    ):
        form.widgets[key].preserve_aspect_ratio = setting

    renamed.update_widget_key(key, "renamed").commit_widget_key_updates()
    assert renamed.widgets["renamed"].preserve_aspect_ratio is preserve
    assert not renamed.widgets["renamed"].hooks_to_trigger

    renamed.fill({"renamed": image})
    same.fill({key: image})
    different.fill({key: image})
    # the image is drawn as without renaming, and the setting changes it
    assert page_contents(renamed) == page_contents(same)
    assert page_contents(renamed) != page_contents(different)
