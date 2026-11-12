# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from pikepdf import Array, Dictionary, Pdf, String
from pypdf import PdfReader

from PyPDFForm import Fields, PdfWrapper, RawElements
from PyPDFForm.lib.patterns import get_widget_key


def test_register_font_no_form_fields(
    pdf_samples, sample_font_stream, request, assert_same_pdf
):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_register_font_no_form_fields.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
        obj.register_font("new_font", sample_font_stream).bulk_create_fields(
            [Fields.TextField(name="foo", page_number=1, x=100, y=100, font="new_font")]
        )
        obj.draw([RawElements.RawText("foo", 1, 200, 200, font="new_font")])

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert_same_pdf(obj.read(), expected)


def test_set_text_field_font_sejda(
    pdf_samples, font_samples, sejda_template, request, assert_same_pdf
):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_font_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template).register_font(
            "new_font", os.path.join(font_samples, "LiberationSerif-Italic.ttf")
        )
        obj.register_font(
            "new_font_2", os.path.join(font_samples, "LiberationSerif-Bold.ttf")
        )
        obj.widgets["buyer_name"].font = "new_font_2"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert_same_pdf(obj.read(), expected)


def test_set_text_field_font_size_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_font_size_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].font_size = 30

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_font_color_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_font_color_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].font_color = (1, 0, 0)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_alignment_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_alignment_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].alignment = 2

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_max_length_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_max_length_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].max_length = 2

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_comb_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_comb_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].max_length = 2
        obj.widgets["buyer_name"].comb = True

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_multiline_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_multiline_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].multiline = True

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_checkbox_size_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_checkbox_size_sejda.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["date_of_this_bill"].size = 30

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_radio_size(pdf_samples, template_with_radiobutton_stream, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_radio_size.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_with_radiobutton_stream)
        obj.widgets["radio_1"].size = 40

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_radio_size_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_radio_size_sejda.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["purchase_option"].size = 40

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_dropdown_font_sejda(
    pdf_samples, dropdown_alignment_sejda, sample_font_stream, request, assert_same_pdf
):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_dropdown_font_sejda.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(dropdown_alignment_sejda)
        obj.register_font("new_font", sample_font_stream)
        obj.widgets["dropdown_left"].font = "new_font"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert_same_pdf(obj.read(), expected)


def test_set_dropdown_font_size_sejda(pdf_samples, dropdown_alignment_sejda, request):
    expected_path = os.path.join(
        pdf_samples, "test_widget_attr_trigger", "test_set_dropdown_font_size_sejda.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(dropdown_alignment_sejda)
        obj.widgets["dropdown_left"].font_size = 30

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_dropdown_font_color_sejda(pdf_samples, dropdown_alignment_sejda, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_dropdown_font_color_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(dropdown_alignment_sejda)
        obj.widgets["dropdown_left"].font_color = (1, 0, 0)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_set_text_field_required_sejda(pdf_samples, sejda_template, request):
    expected_path = os.path.join(
        pdf_samples,
        "test_widget_attr_trigger",
        "test_set_text_field_required_sejda.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_address"].required = True

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


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


def _find_widget(stream, name):
    # the widget annotation of a field, by its short name
    for page in PdfReader(BytesIO(stream)).pages:
        for annot in page.get("/Annots", []):
            annot = annot.get_object()
            if get_widget_key(annot, False) == name:
                return annot

    pytest.fail(f"No widget named {name}.")


def test_clear_absent_text_field_properties(template_stream):
    obj = PdfWrapper(template_stream)
    entries = ("/Ff", "/TU", "/MaxLen", "/Q")
    annot = _find_widget(obj.read(), "test")
    expected = {entry: annot.get(entry) for entry in entries}
    widget = obj.widgets["test"]
    widget.multiline = False
    widget.comb = False
    widget.tooltip = None
    widget.max_length = None
    widget.alignment = None

    # clearing entries the field doesn't have leaves the field unchanged
    annot = _find_widget(obj.read(), "test")
    assert {entry: annot.get(entry) for entry in entries} == expected


@pytest.mark.parametrize(
    ("template", "key", "name", "value", "error"),
    [
        ("sample_template.pdf", "test", "readonly", None, TypeError),
        ("sample_template.pdf", "test", "required", None, TypeError),
        ("sample_template.pdf", "test", "hidden", None, TypeError),
        ("sample_template.pdf", "test", "multiline", None, TypeError),
        ("sample_template.pdf", "test", "comb", None, TypeError),
        ("sample_template.pdf", "test", "max_length", 0, ValueError),
        ("sample_template.pdf", "test", "max_length", -1, ValueError),
        ("sample_template_with_radio_button.pdf", "radio_1", "x", None, TypeError),
        ("sample_template_with_radio_button.pdf", "radio_1", "x", [1, 2], TypeError),
        (
            os.path.join("dropdown", "sample_template_with_dropdown.pdf"),
            "dropdown_1",
            "choices",
            None,
            TypeError,
        ),
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


def _pdf_value(value):
    return String(value) if isinstance(value, str) else value


def _set_parent_entry(stream, name, entry, value):
    # sets the entry on the parent field of a widget without a name
    with Pdf.open(BytesIO(stream)) as pdf:
        for page in pdf.pages:
            for annot in page.get("/Annots", []):
                if "/Parent" in annot and str(annot.Parent.get("/T")) == name:
                    annot.Parent[entry] = _pdf_value(value)

        with BytesIO() as f:
            pdf.save(f)
            return f.getvalue()


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
    stream = _set_parent_entry(
        sample_template_with_full_key, "Date mois", entry, parent
    )
    assert _find_widget(stream, "Date mois").get_inherited(entry) == parent

    obj = PdfWrapper(stream)
    setattr(obj.widgets["Date mois"], name, value)
    assert _find_widget(obj.read(), "Date mois").get_inherited(entry) == value

    setattr(obj.widgets["Date mois"], name, None)
    assert _find_widget(obj.read(), "Date mois").get_inherited(entry) is None
    assert_widgets_match_output(obj)


def _group_fields(stream, names, entry, value):
    # make the fields kids of a parent field that sets the entry
    with Pdf.open(BytesIO(stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        kids = [field for field in fields if str(field.get("/T")) in names]
        parent = pdf.make_indirect(
            Dictionary(
                {
                    "/T": String("group"),
                    "/Kids": Array(kids),
                    entry: _pdf_value(value),
                }
            )
        )
        for kid in kids:
            kid.Parent = parent
        pdf.Root.AcroForm.Fields = Array(
            [field for field in fields if str(field.get("/T")) not in names] + [parent]
        )

        with BytesIO() as f:
            pdf.save(f)
            return f.getvalue()


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize(
    ("name", "entry", "parent", "value"),
    [
        ("max_length", "/MaxLen", 1, 5),
        ("alignment", "/Q", 1, 2),
        ("tooltip", "/TU", "shared tooltip", "own tooltip"),
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
    stream = _group_fields(template_stream, ("test", "test_2"), entry, parent)
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    widget = obj.widgets["group.test" if use_full_widget_name else "test"]
    # a value of its own is set on the widget, leaving the parent's
    setattr(widget, name, value)
    expected = obj.read()
    assert _find_widget(expected, "test").get_inherited(entry) == value

    setattr(widget, name, None)
    # removing it from the parent would change "test_2" too
    with pytest.raises(ValueError, match=f"Cannot remove {entry}"):
        obj.read()

    assert getattr(widget, name) == value
    assert not widget.hooks_to_trigger
    assert obj.read() == expected
    assert _find_widget(expected, "test_2").get_inherited(entry) == parent
    assert_widgets_match_output(obj)
