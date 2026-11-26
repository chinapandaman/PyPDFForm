# -*- coding: utf-8 -*-

import decimal
import os
from io import BytesIO

import pytest
from pikepdf import Array, Dictionary, Name, Object, Pdf, String
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    TextStringObject,
)

from PyPDFForm import Fields, PdfWrapper, RawElements
from PyPDFForm.lib import wrapper
from PyPDFForm.lib.constants import (
    COMB,
    MULTILINE,
    PUSHBUTTON,
    RADIO,
    READ_ONLY,
    REQUIRED,
)
from PyPDFForm.lib.field_tree import get_field_keys
from PyPDFForm.lib.hooks import update_field_readonly
from PyPDFForm.lib.middleware.checkbox import Checkbox
from PyPDFForm.lib.middleware.radio import Radio
from PyPDFForm.lib.middleware.signature import Signature
from PyPDFForm.lib.middleware.text import Text
from PyPDFForm.lib.patterns import get_widget_key
from PyPDFForm.lib.utils import get_version, set_version
from PyPDFForm.lib.wrapper import PdfArray


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


def test_draw_and_coordinate_grid_keep_registered_fonts(
    template_stream, sample_font_stream
):
    obj = PdfWrapper(template_stream).register_font("new_font", sample_font_stream)
    with Pdf.open(BytesIO(obj.read())) as pdf:
        fonts = set(pdf.Root.AcroForm.DR.Font.keys())

    for _ in range(2):
        obj.draw([RawElements.RawText("foo", 1, 100, 100, font="new_font")])
        obj.generate_coordinate_grid()
    obj.widgets["test"].font = "new_font"
    obj.fill({"test": "foo"})
    obj.draw([RawElements.RawText("bar", 2, 100, 100, font="new_font")])

    with Pdf.open(BytesIO(obj.read())) as pdf:
        dr_fonts = pdf.Root.AcroForm.DR.Font
        assert set(dr_fonts.keys()) == fonts

        widget = next(each for each in pdf.pages[0].Annots if each.T == "test")
        assert dr_fonts[str(widget.DA).split()[0]].BaseFont == (
            "/LiberationSerif-BoldItalic"
        )
        assert any(
            str(font.BaseFont).endswith("LiberationSerif-BoldItalic")
            for font in pdf.pages[1].Resources.Font.values()
        )


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


def _set_null_entries(stream, entries):
    # sets entries of widgets, by short name, to null
    writer = PdfWriter(BytesIO(stream))
    for page in writer.pages:
        for annot in page.get("/Annots", []):
            annot = annot.get_object()
            for key in entries.get(get_widget_key(annot, False), ()):
                annot[NameObject(key)] = NullObject()

    with BytesIO() as f:
        writer.write(f)
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


@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_tooltip_of_shared_parent_is_not_inherited(
    template_stream, use_full_widget_name, assert_widgets_match_output
):
    stream = _group_fields(template_stream, ("test", "test_2"), "/TU", "shared tooltip")
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    widget = obj.widgets["group.test" if use_full_widget_name else "test"]
    # the tooltip is the alternate name of "group", not of its kids
    assert widget.tooltip is None

    widget.tooltip = "own tooltip"
    assert _find_widget(obj.read(), "test")["/TU"] == "own tooltip"
    widget.tooltip = None
    output = obj.read()

    assert "/TU" not in _find_widget(output, "test")
    assert _find_widget(output, "test")["/Parent"]["/TU"] == "shared tooltip"
    assert_widgets_match_output(obj)


def test_tooltip_of_field_and_its_widget(
    sample_template_with_full_key, assert_widgets_match_output
):
    # the widget of "Date mois" has no name, so its parent is the field
    stream = _set_parent_entry(
        sample_template_with_full_key, "Date mois", "/TU", "field tooltip"
    )
    obj = PdfWrapper(stream)
    assert obj.widgets["Date mois"].tooltip == "field tooltip"

    # a new tooltip goes to the field, which every widget of it reads
    obj.widgets["Date mois"].tooltip = "new tooltip"
    annot = _find_widget(obj.read(), "Date mois")
    assert "/TU" not in annot
    assert annot["/Parent"]["/TU"] == "new tooltip"
    assert_widgets_match_output(obj)

    # one on the widget, as earlier versions wrote it, is read first and changed
    with Pdf.open(BytesIO(stream)) as pdf:
        for page in pdf.pages:
            for each in page.get("/Annots", []):
                if str(each.get("/Parent", {}).get("/T")) == "Date mois":
                    each.TU = String("widget tooltip")
        stream = _save(pdf)
    obj = PdfWrapper(stream)
    assert obj.widgets["Date mois"].tooltip == "widget tooltip"
    obj.widgets["Date mois"].tooltip = "new tooltip"
    annot = _find_widget(obj.read(), "Date mois")
    assert annot["/TU"] == "new tooltip"
    assert annot["/Parent"]["/TU"] == "field tooltip"


def test_null_tooltip(template_stream):
    # a null tooltip is absent
    stream = _set_null_entries(template_stream, {"test": ["/TU"]})
    assert PdfWrapper(stream).widgets["test"].tooltip is None


def test_version_leaves_failing_comb_change_to_read(template_stream):
    stream = _with_parent_cycle(template_stream, "test")
    # below 1.5, the version getter previews queued comb changes
    obj = PdfWrapper(set_version(stream, get_version(stream), "1.4"))
    widget = obj.widgets["test"]
    widget.comb = True

    assert obj.version == "1.4"
    assert widget.hooks_to_trigger

    with pytest.raises(ValueError, match="the /Parent chain of the field has a cycle"):
        obj.read()
    assert widget.comb is False


def _save(pdf):
    with BytesIO() as f:
        pdf.save(f)
        return f.getvalue()


def _set_default_appearance(stream, name, default_appearance):
    # sets the /DA of a field whose widget has its name
    with Pdf.open(BytesIO(stream)) as pdf:
        for field in pdf.Root.AcroForm.Fields:
            if str(field.get("/T")) == name:
                field.DA = _pdf_value(default_appearance)

        return _save(pdf)


# chosen by the lookup, then changed: font size 20, red, or the /Helv font
CHOSEN_DA = "/Cour 9 Tf 0 0 1 rg"
OTHER_DA = "/Helv 5 Tf 0 g"


def _nest_fields(stream, values, entry="/DA"):
    # makes "test" and "test_2" kids of "inner", a kid of "outer", and sets the
    # entry of "test", "inner", "outer", or the AcroForm as given, without others
    with Pdf.open(BytesIO(stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        kids = [field for field in fields if str(field.get("/T")) in ("test", "test_2")]
        inner = pdf.make_indirect(
            Dictionary({"/T": String("inner"), "/Kids": Array(kids)})
        )
        outer = pdf.make_indirect(
            Dictionary({"/T": String("outer"), "/Kids": Array([inner])})
        )
        inner.Parent = outer
        for kid in kids:
            kid.Parent = inner
            if entry in kid:
                del kid[entry]
        pdf.Root.AcroForm.Fields = Array(
            [field for field in fields if field not in kids] + [outer]
        )
        if entry in pdf.Root.AcroForm:
            del pdf.Root.AcroForm[entry]

        holders = {
            "test": next(kid for kid in kids if str(kid.T) == "test"),
            "inner": inner,
            "outer": outer,
            "/AcroForm": pdf.Root.AcroForm,
        }
        for holder, value in values.items():
            holders[holder][entry] = _pdf_value(value)

        return _save(pdf)


def _get_nested_entries(stream, entry="/DA"):
    # the entry of each field of _nest_fields, or None without one
    reader = PdfReader(BytesIO(stream))
    inner = _find_widget(stream, "test")["/Parent"].get_object()
    return {
        "test": _find_widget(stream, "test").get(entry),
        "test_2": _find_widget(stream, "test_2").get(entry),
        "inner": inner.get(entry),
        "outer": inner["/Parent"].get_object().get(entry),
        "/AcroForm": reader.root_object["/AcroForm"].get(entry),
    }


def _put_under_outer(stream, names, entries):
    # makes "outer" the parent of the fields with these names, in this order,
    # and moves the entries from them to "outer"
    with Pdf.open(BytesIO(stream)) as pdf:
        kids = [_get_field(pdf, name) for name in names]
        outer = pdf.make_indirect(
            Dictionary({"/T": String("outer"), "/Kids": Array(kids)})
        )
        for entry, value in entries.items():
            for kid in kids:
                if entry in kid:
                    del kid[entry]
            outer[entry] = _pdf_value(value)
        for kid in kids:
            kid.Parent = outer
        pdf.Root.AcroForm.Fields = Array(
            [each for each in pdf.Root.AcroForm.Fields if each not in kids] + [outer]
        )

        return _save(pdf)


def _split_widgets(pdf, field, count=1):
    # the widget merged with the field becomes kids without a name, in its
    # place on its page, which take the field's entries from the field
    widgets = []
    for index in range(count):
        widget = pdf.make_indirect(Dictionary(field))
        for key in ("/T", "/FT", "/Ff", "/V", "/DA", "/Opt", "/Parent", "/Kids"):
            if key in widget:
                del widget[key]
        widget.Parent = field
        if index:
            widget.Rect = Array([10, 10 + 30 * index, 100, 30 + 30 * index])
        widgets.append(widget)
    for key in ("/Type", "/Subtype", "/Rect", "/AP", "/MK", "/P", "/F"):
        if key in field:
            del field[key]
    field.Kids = Array(widgets)
    for page in pdf.pages:
        annots = list(page.get("/Annots", []))
        if field in annots:
            index = annots.index(field)
            page.Annots = Array(annots[:index] + widgets + annots[index + 1 :])

    return widgets


@pytest.mark.parametrize("use_full_widget_name", [False, True])
@pytest.mark.parametrize(
    ("name", "value", "expected"),
    [
        ("font_size", 20, "/Cour 20 Tf 0 0 1 rg"),
        ("font_color", (1, 0, 0), "/Cour 9 Tf 1 0 0 rg"),
        ("font", "/Helv", "/Helv 9 Tf 0 0 1 rg"),
    ],
)
@pytest.mark.parametrize(
    "default_appearances",
    [
        {"/AcroForm": CHOSEN_DA},
        {"/AcroForm": OTHER_DA, "outer": CHOSEN_DA},
        {"/AcroForm": OTHER_DA, "outer": OTHER_DA, "inner": CHOSEN_DA},
        # the widget's own /DA takes precedence over its fields'
        {"/AcroForm": OTHER_DA, "inner": OTHER_DA, "test": CHOSEN_DA},
    ],
    ids=["acroform", "grandparent", "parent", "widget"],
)
def test_change_inherited_default_appearance(
    template_stream,
    default_appearances,
    name,
    value,
    expected,
    use_full_widget_name,
    assert_widgets_match_output,
):
    stream = _nest_fields(template_stream, default_appearances)
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    widget = obj.widgets["outer.inner.test" if use_full_widget_name else "test"]
    # the /DA that the change edits is the one read
    assert (widget.font, widget.font_size, widget.font_color) == ("/Cour", 9, (0, 0, 1))

    setattr(widget, name, value)
    result = _get_nested_entries(obj.read())

    # only the widget's own field changes; fields shared with "test_2" and the
    # AcroForm default don't
    assert result == {
        "test": expected,
        "test_2": None,
        "inner": default_appearances.get("inner"),
        "outer": default_appearances.get("outer"),
        "/AcroForm": default_appearances["/AcroForm"],
    }
    assert_widgets_match_output(obj)

    # appearance generation uses the changed /DA
    filled = PdfWrapper(
        obj.read(),
        use_full_widget_name=use_full_widget_name,
        generate_appearance_streams=True,
    ).fill({"outer.inner.test" if use_full_widget_name else "test": "foo"})
    appearance = _find_widget(filled.read(), "test")["/AP"]["/N"].get_data()
    assert f"\n{expected}\n".encode() in appearance


@pytest.mark.parametrize(
    ("parent", "expected"),
    [("/Cour  0 Tf 0 g", "/Cour  20 Tf 0 g"), (None, "/Helv 20 Tf 0 g ")],
    ids=["field", "acroform"],
)
def test_change_default_appearance_of_kid_widget(
    sample_template_with_full_key, parent, expected
):
    # the widget of "Date mois" has no name, so its parent is the field
    stream = sample_template_with_full_key
    if parent is None:
        with Pdf.open(BytesIO(stream)) as pdf:
            for page in pdf.pages:
                for annot in page.get("/Annots", []):
                    if (
                        "/Parent" in annot
                        and str(annot.Parent.get("/T")) == "Date mois"
                    ):
                        del annot.Parent["/DA"]
            stream = _save(pdf)

    obj = PdfWrapper(stream)
    obj.widgets["Date mois"].font_size = 20
    widget = _find_widget(obj.read(), "Date mois")

    assert "/DA" not in widget
    assert widget["/Parent"].get_object()["/DA"] == expected
    assert (
        PdfReader(BytesIO(obj.read())).root_object["/AcroForm"]["/DA"]
        == "/Helv 0 Tf 0 g "
    )


def test_change_inherited_dropdown_default_appearance(
    sample_template_with_dropdown, assert_widgets_match_output
):
    with Pdf.open(BytesIO(sample_template_with_dropdown)) as pdf:
        for field in pdf.Root.AcroForm.Fields:
            if str(field.get("/T")) == "dropdown_1":
                del field["/DA"]
        pdf.Root.AcroForm.DA = String("/Helv 0 Tf 0 g")
        stream = _save(pdf)

    obj = PdfWrapper(stream)
    widget = obj.widgets["dropdown_1"]
    assert (widget.font, widget.font_size, widget.font_color) == ("/Helv", 0, (0, 0, 0))
    widget.font_size = 20
    widget.font_color = (1, 0, 0)

    assert _find_widget(obj.read(), "dropdown_1")["/DA"] == "/Helv 20 Tf 1 0 0 rg"
    assert (
        PdfReader(BytesIO(obj.read())).root_object["/AcroForm"]["/DA"]
        == "/Helv 0 Tf 0 g"
    )
    assert_widgets_match_output(obj)


@pytest.mark.parametrize(
    ("default_appearance", "name", "value", "expected"),
    [
        ("/Helv 12  Tf 0 g", "font_size", 20, "/Helv 20  Tf 0 g"),
        ("/Helv 12 Tf\n0 g", "font_color", (1, 0, 0), "/Helv 12 Tf\n1 0 0 rg"),
        (
            ".2666667 .2666667 .2666667 rg\n/F0 8 Tf\n",
            "font_color",
            (1, 0, 0),
            "1 0 0 rg\n/F0 8 Tf\n",
        ),
        ("/Helv 12 Tf 0 g 2 Tz", "font_color", (1, 0, 0), "/Helv 12 Tf 1 0 0 rg 2 Tz"),
        ("/Helv 12 Tf 0 0 0 .9 k", "font_color", (0, 0, 1), "/Helv 12 Tf 0 0 1 rg"),
        ("/Helv 12 Tf", "font_color", (1, 0, 0), "/Helv 12 Tf 1 0 0 rg"),
        ("1 0 0 rg ", "font_color", (0, 0, 1), "0 0 1 rg "),
        ("", "font_color", (1, 0, 0), "1 0 0 rg"),
        # a font name without its slash, as some producers write it
        ("Courier 12 Tf .1 .1 .1 rg", "font", "/Helv", "/Helv 12 Tf .1 .1 .1 rg"),
        ("Courier 12 Tf .1 .1 .1 rg", "font_size", 20, "Courier 20 Tf .1 .1 .1 rg"),
        (
            "/ZaDb 5.6 Tf 0 g /Helv 5.6 Tf 0 g",
            "font_size",
            9,
            "/ZaDb 9 Tf 0 g /Helv 9 Tf 0 g",
        ),
        (
            "/ZaDb 5.6 Tf 0 g /Helv 5.6 Tf 0 g",
            "font_color",
            (1, 0, 0),
            "/ZaDb 5.6 Tf 1 0 0 rg /Helv 5.6 Tf 1 0 0 rg",
        ),
        ("/Helv 12 Tf 0 g % gray", "font_size", 20, "/Helv 20 Tf 0 g % gray"),
        # a later color space operation takes effect after the replaced color
        (
            "/Arial 12 Tf 0 g /DeviceRGB cs 0 0 1 sc",
            "font_color",
            (1, 0, 0),
            "/Arial 12 Tf 1 0 0 rg /DeviceRGB cs 0 0 1 sc 1 0 0 rg",
        ),
        (
            "/Arial 12 Tf /DeviceRGB cs 0 0 1 sc 2 Tz",
            "font_color",
            (1, 0, 0),
            "/Arial 12 Tf /DeviceRGB cs 0 0 1 sc 1 0 0 rg 2 Tz",
        ),
        # a dash pattern, and an array in an array
        (
            "/Arial 12 Tf 0 g 2 Tr [2 3] 0 d",
            "font_size",
            14,
            "/Arial 14 Tf 0 g 2 Tr [2 3] 0 d",
        ),
        ("/Arial 12 Tf [[1] /X] 0 d", "font", "/Helv", "/Helv 12 Tf [[1] /X] 0 d"),
        # strings and dictionaries are kept as they are
        (
            "/Tx <</MCID 0>> BDC /Arial 12 Tf (a\\) Tj) Tj <41> Tj 0 g",
            "font_color",
            (0, 0, 1),
            "/Tx <</MCID 0>> BDC /Arial 12 Tf (a\\) Tj) Tj <41> Tj 0 0 1 rg",
        ),
        ("/Arial 12 Tf [(x]) 2] TJ", "font_size", 9, "/Arial 9 Tf [(x]) 2] TJ"),
        # numbers are written without an exponent
        ("/Arial 12 Tf 0 g", "font_size", 1e-5, "/Arial 0.00001 Tf 0 g"),
        (
            "/Arial 12 Tf 0 g",
            "font_color",
            (1e-5, 0, 2.5e-7),
            "/Arial 12 Tf 0.00001 0 0.00000025 rg",
        ),
        # digits of other scripts are written as ASCII digits
        ("/Arial 9 Tf 0 g", "font_size", "\uff11\uff12", "/Arial 12 Tf 0 g"),
        (
            "/Arial 9 Tf 0 g",
            "font_color",
            ("\uff10", "\uff10", "\uff11"),
            "/Arial 9 Tf 0 0 1 rg",
        ),
        ("/Arial 9 Tf 0 g", "font", "/My#20Font", "/My#20Font 9 Tf 0 g"),
        # the CLI passes a list
        ("/Helv 12 Tf 0 g", "font_color", [0, 0, 1], "/Helv 12 Tf 0 0 1 rg"),
        # a NUL separator makes pypdf read a byte string
        (String(b"/Arial\x0012 Tf 0 g"), "font_size", 14, b"/Arial\x0014 Tf 0 g"),
    ],
)
def test_change_default_appearance_operands(
    template_stream, default_appearance, name, value, expected
):
    obj = PdfWrapper(
        _set_default_appearance(template_stream, "test", default_appearance)
    )
    setattr(obj.widgets["test"], name, value)

    assert _find_widget(obj.read(), "test")["/DA"] == expected


def _with_parent_cycle(stream, name):
    # the field's /DA is removed, and its parent is its own parent
    with Pdf.open(BytesIO(stream)) as pdf:
        for field in pdf.Root.AcroForm.Fields:
            if str(field.get("/T")) == name:
                parent = pdf.make_indirect(Dictionary({"/Kids": Array([field])}))
                parent.Parent = parent
                field.Parent = parent
                del field["/DA"]

        return _save(pdf)


@pytest.mark.parametrize(
    ("default_appearance", "expected"),
    [
        ("/Helv 12 Tf 0 g", ("/Helv", 12, (0, 0, 0))),
        (
            ".2666667 .2666667 .2666667 rg\n/F0 8 Tf\n",
            ("/F0", 8, (0.2666667, 0.2666667, 0.2666667)),
        ),
        # CMYK is converted to RGB, each component 1 - min(1, color + black)
        ("/Helv 10.5 Tf 0 0 0 .9 k", ("/Helv", 10.5, (0.1, 0.1, 0.1))),
        ("/Helv 0 Tf 1 .5 0 .5 k", ("/Helv", 0, (0, 0, 0.5))),
        ("Courier 12 Tf .1 .1 .1 rg", ("Courier", 12, (0.1, 0.1, 0.1))),
        ("/My#20Font 12.0 Tf 0 g", ("/My#20Font", 12, (0, 0, 0))),
        # the last font and the last fill color take effect
        ("/ZaDb 5.6 Tf 0 g /Helv 9 Tf 1 0 0 rg", ("/Helv", 9, (1, 0, 0))),
        ("/Arial 12 Tf 0 g /DeviceRGB cs 0 0 1 sc", ("/Arial", 12, None)),
        ("/Arial 12 Tf /DeviceRGB cs 0 0 1 sc 0 0 1 rg", ("/Arial", 12, (0, 0, 1))),
        ("/Helv 12 Tf", ("/Helv", 12, None)),
        ("0 g", (None, None, (0, 0, 0))),
        ("/Helv Tf 0 g", (None, None, (0, 0, 0))),
        ("/Helv 12 Tf 0 0 g", ("/Helv", 12, None)),
        # strings and dictionaries are read as single operands
        ("/Helv 12 Tf (x) Tj", ("/Helv", 12, None)),
        ("(a \\) (b) c) Tj /F1 9 Tf <</MCID 0>> BDC 0 g", ("/F1", 9, (0, 0, 0))),
        ("[(a]) <41>] TJ /F1 8.5 Tf (%) Tj 1 0 0 rg", ("/F1", 8.5, (1, 0, 0))),
        ("/Helv 12 Tf {0} 0 g", (None, None, None)),
        (String(b"/Arial\x0012 Tf 0 g"), ("/Arial", 12, (0, 0, 0))),
        (12, (None, None, None)),
        # a name isn't a string, although it reads as one
        (Name("/Arial 12 Tf 0 g"), (None, None, None)),
        (None, (None, None, None)),
    ],
)
def test_read_default_appearance(template_stream, default_appearance, expected):
    stream = (
        _with_parent_cycle(template_stream, "test")
        if default_appearance is None
        else _set_default_appearance(template_stream, "test", default_appearance)
    )
    widget = PdfWrapper(stream).widgets["test"]

    assert (widget.font, widget.font_size, widget.font_color) == expected


def test_default_appearance_in_any_decimal_context(template_stream):
    stream = _set_default_appearance(
        template_stream, "test", "/Helv 12.5 Tf 0 0 0 .9876 k"
    )
    # a caller's context with little precision, which traps rounding
    with decimal.localcontext(prec=2) as context:
        context.traps[decimal.Inexact] = True
        obj = PdfWrapper(stream)
        widget = obj.widgets["test"]
        assert widget.font_size == 12.5
        assert widget.font_color == (0.0124, 0.0124, 0.0124)

        widget.font_size = 1.23456
        widget.font_color = (0.98765, 0, 1e-5)
        assert (
            _find_widget(obj.read(), "test")["/DA"]
            == "/Helv 1.23456 Tf 0.98765 0 0.00001 rg"
        )


@pytest.mark.parametrize(
    ("default_appearance", "name", "value", "message"),
    [
        ("0 g", "font_size", 20, "has no Tf operator"),
        ("0 g", "font", "/Helv", "has no Tf operator"),
        ("/Helv Tf 0 g", "font_size", 20, "needs a font and a font size"),
        ("12 Tf 0 g", "font", "/Helv", "needs a font and a font size"),
        ("/Helv /F1 Tf 0 g", "font_size", 20, "needs a font and a font size"),
        ("/Helv 12 Tf (x 0 g", "font_size", 20, r"unclosed '\('"),
        # an escaped backslash doesn't escape the parenthesis after it
        ("/Helv 12 Tf (x\\\\) y) Tj", "font_size", 20, r"unexpected '\)'"),
        ("/Helv 12 Tf <</A 1 0 g", "font_size", 20, "unclosed '<<'"),
        ("/Helv 12 Tf <</A [1>>] 0 g", "font_size", 20, "unexpected '>'"),
        ("/Helv 12 Tf <4G> Tj 0 g", "font_size", 20, "unexpected '<'"),
        ("/Helv 12 Tf {0} 0 g", "font_size", 20, r"unexpected '\{'"),
        # a string operand isn't changed
        ("(Helv) 12 Tf 0 g", "font", "/Cour", "needs a font and a font size"),
        ("/Helv 12 Tf (0) g", "font_color", (1, 0, 0), "g operator .* needs 1 number"),
        ("/Helv 12 Tf 0", "font_color", (1, 0, 0), "ends with operands"),
        ("/Helv 12 Tf 0 0 g", "font_color", (1, 0, 0), "g operator .* needs 1 number"),
        ("/Helv 12 Tf /X 0 0 rg", "font_color", (1, 0, 0), "needs 3 numbers"),
        ("/Helv 12 Tf [2 3 0 d", "font_size", 20, r"unclosed '\['"),
        ("/Helv 12 Tf 2] 0 d", "font_size", 20, r"unexpected '\]'"),
        ("[/Helv] 12 Tf", "font", "/Cour", "needs a font and a font size"),
        ("/Helv 12 Tf 0 g", "font_size", float("inf"), "is not a number a PDF"),
        ("/Helv 12 Tf 0 g", "font_color", (float("nan"), 0, 0), "is not a number"),
        ("/Helv 12 Tf 0 g", "font_color", (1, 0, "red"), "is not a number"),
        ("/Helv 12 Tf 0 g", "font_color", (1, 0), "with three components"),
        ("/Helv 12 Tf 0 g", "font_color", (1, 0, 0, 0), "with three components"),
        ("/Helv 12 Tf 0 g", "font_color", 0.5, "with three components"),
        ("/Helv 12 Tf 0 g", "font", "/My Font", "is not a PDF name"),
        ("/Helv 12 Tf 0 g", "font", "/\u4e2d", "is not a PDF name"),
        ("/Helv 12 Tf 0 g", "font", "/Arial#", "is not a PDF name"),
        ("/Helv 12 Tf 0 g", "font", "/Arial#00", "is not a PDF name"),
        ("/Helv 12 Tf 0 g", "font", "/Arial#4G", "is not a PDF name"),
        ("/Arial \uff11\uff12 Tf 0 g", "font_size", 20, "needs a font and a font size"),
        (12, "font_size", 20, "is not a string"),
        (Name("/Arial 12 Tf 0 g"), "font_size", 20, "is not a string"),
        (None, "font_size", 20, "the /Parent chain of the field has a cycle"),
    ],
)
def test_change_default_appearance_errors(
    template_stream,
    default_appearance,
    name,
    value,
    message,
    assert_widgets_match_output,
):
    stream = (
        _with_parent_cycle(template_stream, "test")
        if default_appearance is None
        else _set_default_appearance(template_stream, "test", default_appearance)
    )
    obj = PdfWrapper(stream)
    original = obj.read()
    read_value = getattr(obj.widgets["test"], name)
    # applied before the failing change, and discarded with it
    obj.widgets["test"].alignment = 2
    setattr(obj.widgets["test"], name, value)

    with pytest.raises(ValueError, match=message):
        obj.read()

    assert obj.widgets["test"].alignment is None
    # the value read from the PDF is restored
    assert getattr(obj.widgets["test"], name) == read_value
    assert not obj.widgets["test"].hooks_to_trigger
    assert obj.read() == original
    assert_widgets_match_output(obj)


@pytest.mark.parametrize(
    ("name", "value"),
    [("font_size", 1e-5), ("font_size", 1e20), ("font_color", (1e-5, 0, 0))],
)
def test_change_default_appearance_again(template_stream, name, value):
    # a changed /DA can be changed again
    obj = PdfWrapper(template_stream)
    setattr(obj.widgets["test"], name, value)
    obj.read()
    obj.widgets["test"].font_size = 12
    obj.widgets["test"].font_color = (0, 0, 1)

    assert _find_widget(obj.read(), "test")["/DA"] == "/Arial 12 Tf 0 0 1 rg"


def _with_null_default_appearance(stream, acroform_null):
    # the field's /DA is null, and the AcroForm's too if acroform_null
    writer = PdfWriter(BytesIO(stream))
    if acroform_null:
        writer.root_object["/AcroForm"][NameObject("/DA")] = NullObject()
    for annot in writer.pages[0]["/Annots"]:
        annot = annot.get_object()
        if annot.get("/T") == "test":
            annot[NameObject("/DA")] = NullObject()

    with BytesIO() as f:
        writer.write(f)
        return f.getvalue()


def test_change_default_appearance_over_null(template_stream):
    # a null /DA is absent, so the AcroForm default is used
    obj = PdfWrapper(_with_null_default_appearance(template_stream, False))
    widget = obj.widgets["test"]
    assert (widget.font, widget.font_size, widget.font_color) == ("/Helv", 0, (0, 0, 0))
    widget.font_size = 14

    assert _find_widget(obj.read(), "test")["/DA"] == "/Helv 14 Tf 0 g "

    obj = PdfWrapper(_with_null_default_appearance(template_stream, True))
    widget = obj.widgets["test"]
    assert (widget.font, widget.font_size, widget.font_color) == (None, None, None)
    widget.font_size = 14
    with pytest.raises(ValueError, match="neither the field nor the form sets one"):
        obj.read()


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("/My Font", "/My#20Font 0 Tf 0 g"),
        ("/My#Font", "/My#23Font 0 Tf 0 g"),
        ("/\u4e2d", "/#E4#B8#AD 0 Tf 0 g"),
    ],
)
def test_change_font_to_resource_with_escaped_name(template_stream, key, expected):
    # the font's resource key has characters that a PDF name escapes
    with Pdf.open(BytesIO(template_stream)) as pdf:
        pdf.Root.AcroForm.DR.Font[Name(key)] = pdf.make_indirect(
            Dictionary(Type=Name.Font, Subtype=Name.Type1, BaseFont=Name.Courier)
        )
        stream = _save(pdf)

    obj = PdfWrapper(stream)
    assert "Courier" in obj.fonts
    obj.widgets["test"].font = "Courier"
    default_appearance = _find_widget(obj.read(), "test")["/DA"]

    assert default_appearance == expected
    # the name in /DA is the resource key
    assert Object.parse(default_appearance.split(" ")[0].encode()) == Name(key)


@pytest.mark.parametrize("key", ["test", "dropdown_1"])
@pytest.mark.parametrize("font", ["nonexistent", "Liberation Serif"])
def test_change_font_to_unknown_name(
    template_stream,
    sample_template_with_dropdown,
    sample_font_stream,
    key,
    font,
    assert_widgets_match_output,
):
    obj = PdfWrapper(
        template_stream if key == "test" else sample_template_with_dropdown
    ).register_font("new_font", sample_font_stream)
    original = obj.read()
    widget = obj.widgets[key]
    read_style = (widget.font, widget.font_size)
    # applied before the failing change, and discarded with it
    widget.font_size = 20
    widget.font = font

    with pytest.raises(ValueError, match=f"^Cannot change the font: '{font}' is not"):
        obj.read()

    assert (widget.font, widget.font_size) == read_style
    assert not widget.hooks_to_trigger
    assert obj.read() == original
    assert_widgets_match_output(obj)


def test_change_font_keeps_other_fonts_read_from_pdf(
    template_stream, sample_font_stream, assert_widgets_match_output
):
    # "test_2" writes its font without a slash, as the name of a registered
    # font, and "test" uses another font
    stream = _set_default_appearance(template_stream, "test", "/Helv 12 Tf 0 g")
    stream = _set_default_appearance(stream, "test_2", "Courier 10 Tf 0 g")
    obj = PdfWrapper(stream).register_font("Courier", sample_font_stream)
    assert obj.widgets["test_2"].font == "Courier"

    obj.widgets["test"].font = "Courier"
    result = obj.read()
    resource = obj.widgets["test"].font

    # only the font being changed becomes the registered font's resource
    assert resource.startswith("/")
    assert _find_widget(result, "test")["/DA"] == f"{resource} 12 Tf 0 g"
    assert _find_widget(result, "test_2")["/DA"] == "Courier 10 Tf 0 g"
    assert obj.widgets["test_2"].font == "Courier"
    assert_widgets_match_output(obj)


def test_assign_back_font_read_without_slash(template_stream):
    stream = _set_default_appearance(template_stream, "test", "Courier 12 Tf 0 g")
    obj = PdfWrapper(stream)
    assert obj.widgets["test"].font == "Courier"

    # the font the field uses is kept as it is
    obj.widgets["test"].font = obj.widgets["test"].font
    assert _find_widget(obj.read(), "test")["/DA"] == "Courier 12 Tf 0 g"

    # another field doesn't use it, so it is a font the PDF doesn't have
    original = obj.read()
    obj.widgets["test_2"].font = "Courier"
    with pytest.raises(ValueError, match="'Courier' is not a registered font"):
        obj.read()
    assert obj.read() == original


def test_assign_back_font_with_name_of_registered_font(
    template_stream, sample_font_stream
):
    stream = _set_default_appearance(template_stream, "test", "Helvetica 12 Tf 0 g")
    obj = PdfWrapper(stream).register_font("Helvetica", sample_font_stream)
    assert obj.widgets["test"].font == "Helvetica"

    # the font the field uses is kept, not replaced by the registered one
    obj.widgets["test"].font = obj.widgets["test"].font
    assert _find_widget(obj.read(), "test")["/DA"] == "Helvetica 12 Tf 0 g"

    # another field gets the registered font
    obj.widgets["test_2"].font = "Helvetica"
    font = _find_widget(obj.read(), "test_2")["/DA"].split()[0]
    assert font != "Helvetica"
    assert PdfWrapper(obj.read()).widgets["test_2"].font == font


def test_font_change_is_decided_per_annotation(
    template_stream, assert_widgets_match_output
):
    # the PDF's /Helv font has the base font Helvetica
    stream = _set_default_appearance(template_stream, "test", "Helvetica 12 Tf 0 g")

    # a font changed and changed back is looked up again
    obj = PdfWrapper(stream)
    obj.widgets["test"].font = "/Arial"
    obj.widgets["test"].font = "Helvetica"
    assert _find_widget(obj.read(), "test")["/DA"] == "/Helv 12 Tf 0 g"
    assert obj.widgets["test"].font == "/Helv"
    assert_widgets_match_output(obj)

    # only the widget that uses the font keeps it, and the field reads it from
    # its last widget, as reopening does
    with Pdf.open(BytesIO(template_stream)) as pdf:
        widgets = _split_widgets(pdf, _get_field(pdf, "test"), 2)
        for widget, default_appearance in zip(
            widgets, ("/Arial 9 Tf 0 g", "Helvetica 12 Tf 0 g"), strict=True
        ):
            widget.DA = String(default_appearance)
        obj = PdfWrapper(_save(pdf))
    assert obj.widgets["test"].font == "Helvetica"
    obj.widgets["test"].font = obj.widgets["test"].font
    with Pdf.open(BytesIO(obj.read())) as pdf:
        kids = _get_field(pdf, "test").Kids
        assert [str(kid.DA) for kid in kids] == [
            "/Helv 9 Tf 0 g",
            "Helvetica 12 Tf 0 g",
        ]
    assert obj.widgets["test"].font == "Helvetica"
    assert_widgets_match_output(obj)


def test_failed_font_readback_commits_nothing(
    template_stream, monkeypatch, assert_widgets_match_output
):
    obj = PdfWrapper(template_stream)
    original = obj.read()
    font = obj.widgets["test"].font
    obj.widgets["test"].font = "/Helv"

    # reading the changed fonts back fails once, after the hooks applied
    real_build_widgets = wrapper.build_widgets
    error = OSError("injected readback failure")

    def fail(*_args):
        monkeypatch.setattr(wrapper, "build_widgets", real_build_widgets)
        raise error

    monkeypatch.setattr(wrapper, "build_widgets", fail)
    with pytest.raises(OSError, match="injected readback failure"):
        obj.read()

    # the PDF, the widget, and its queue are as before the change
    assert obj.read() == original
    assert obj.widgets["test"].font == font
    assert not obj.widgets["test"].hooks_to_trigger

    # and the change can be made again
    obj.widgets["test"].font = "/Helv"
    assert _find_widget(obj.read(), "test")["/DA"].startswith("/Helv ")
    assert obj.widgets["test"].font == "/Helv"
    assert_widgets_match_output(obj)


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


def _get_field(pdf, name):
    # a field of the AcroForm by its name
    return next(
        field for field in pdf.Root.AcroForm.Fields if str(field.get("/T")) == name
    )


def _set_on_state(widget, state="/Custom"):
    # gives a checkbox widget an on state other than /Yes
    widget.AP.N = Dictionary({"/Off": widget.AP.N.Off, state: widget.AP.N.Yes})


def _get_widget_states(stream, name):
    # the /AS and /V of each widget with the short name, in page order
    return [
        [annot.get("/AS"), annot.get("/V")]
        for page in PdfReader(BytesIO(stream)).pages
        for annot in (each.get_object() for each in page.get("/Annots", []))
        if annot.get("/Subtype") == "/Widget" and get_widget_key(annot, False) == name
    ]


# a flag that no property changes, which a change keeps
OTHER_FLAG = 1 << 22
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
    stream = _nest_fields(template_stream, flags, "/Ff")
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
    assert _get_nested_entries(result, "/Ff") == {
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
    stream = _set_parent_entry(
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
        stream = _save(pdf)

    obj = PdfWrapper(stream)
    assert obj.widgets["Date mois"].readonly
    obj.widgets["Date mois"].readonly = False
    widget = _find_widget(obj.read(), "Date mois")

    # the flags that were found change
    assert widget.get("/Ff") == (OTHER_FLAG if own else None)
    assert widget["/Parent"].get_object()["/Ff"] == OTHER_FLAG
    assert_widgets_match_output(obj)


@pytest.mark.parametrize(("name", "flag"), FLAG_PROPERTIES)
def test_change_field_flag_with_parent_cycle(
    template_stream, name, flag, assert_widgets_match_output
):
    obj = PdfWrapper(_with_parent_cycle(template_stream, "test"))
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
        _get_field(pdf, "test").Ff = flag
        obj = PdfWrapper(_save(pdf))
    assert getattr(obj.widgets["test"], name) is True
    setattr(obj.widgets["test"], name, False)

    assert _find_widget(obj.read(), "test")["/Ff"] == 0


def test_fill_readonly_with_parent_cycle(template_stream):
    obj = PdfWrapper(_with_parent_cycle(template_stream, "test"))
    original = obj.read()

    with pytest.raises(ValueError, match="the /Parent chain of the field has a cycle"):
        obj.fill({"test": "foo", "test_2": "bar"}, readonly=True)

    assert obj.read() == original
    assert obj.widgets["test"].value is None
    assert obj.widgets["test_2"].value is None
    assert obj.widgets["test_2"].readonly is False


def test_change_flag_of_widget_that_is_its_own_parent(template_stream):
    with Pdf.open(BytesIO(template_stream)) as pdf:
        field = _get_field(pdf, "test")
        field.Parent = field
        stream = _save(pdf)

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
    stream = _nest_fields(template_stream, {holder: value}, "/Ff")
    message = "Cannot read the field flags: /Ff .* is not a number"

    # they aren't read as no flags
    with pytest.raises(ValueError, match=message):
        PdfWrapper(stream)

    # nor overwritten by a change
    widget = _find_widget(stream, "test")
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

    assert _find_widget(obj.read(), "test")["/Ff"] == READ_ONLY
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
        radio = _get_field(pdf, "radio_1")
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
        stream = _save(pdf)

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
    field = _find_widget(result, "radio_1")["/Parent"].get_object()
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
        radio = _get_field(pdf, "radio_1")
        radio.DV = Name.Off
        radio.Kids[local].Ff = READ_ONLY
        stream = _save(pdf)

    # every option is classified by its field's flags, whichever comes first
    obj = PdfWrapper(stream)
    assert isinstance(obj.widgets["radio_1"], Radio)
    assert obj.widgets["radio_1"].number_of_options == 2

    obj.widgets["radio_1"].required = True
    reopened = PdfWrapper(obj.read()).widgets["radio_1"]
    assert isinstance(reopened, Radio)
    assert reopened.number_of_options == 2
    assert_widgets_match_output(obj)


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
        _nest_fields(template_stream, holders, "/FT"),
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
        radio = _get_field(pdf, "radio_1")
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
        stream = _save(pdf)

    key = "outer.radio_1" if use_full_widget_name else "radio_1"
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert isinstance(obj.widgets[key], Radio)
    assert obj.widgets[key].number_of_options == 2

    obj.fill({key: 1})
    result = obj.read()
    assert _get_widget_states(result, "radio_1") == [["/Off", None], ["/1", None]]
    assert _find_widget(result, "radio_1")["/Parent"].get_object()["/V"] == "/1"
    assert PdfWrapper(result, use_full_widget_name=use_full_widget_name).data[key] == 1
    assert_widgets_match_output(obj)


@pytest.mark.parametrize("shape", ["group", "mutual", "listing", "three"])
@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_field_type_with_parent_cycle(template_stream, shape, use_full_widget_name):
    # no field of the cycle has a /FT, so the cycle is reached before one is found
    names = ("test", "test_2", "test_3") if shape == "three" else ("test", "test_2")
    with Pdf.open(BytesIO(_with_field_cycle(template_stream, shape))) as pdf:
        for page in pdf.pages:
            for annot in page.Annots:
                if str(annot.get("/T")) in names:
                    del annot["/FT"]
        stream = _save(pdf)

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
        field = _get_field(pdf, "radio_1")
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
        stream = _save(pdf)

    assert type(PdfWrapper(stream).widgets["radio_1"]) is _type


def _with_button_parent(stream, shape):
    # "check_2" gets the /Parent "check", a button field that doesn't list it
    with Pdf.open(BytesIO(stream)) as pdf:
        check, check_2 = _get_field(pdf, "check"), _get_field(pdf, "check_2")
        check_2.Parent = check
        if shape == "unnamed":
            del check_2.T
        elif shape == "cycle":
            # "check" also sets the radio flag, lists "check_2" as a kid, and
            # has "check_2" as its own parent
            check.Parent = check_2
            check.Kids = Array([check_2])
            check.Ff = RADIO

        return _save(pdf)


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
        _with_button_parent(template_stream, shape),
        use_full_widget_name=use_full_widget_name,
    )
    assert type(obj.widgets[key]) is _type
    before = obj.data

    obj.fill({key: value})
    result = obj.read()
    for name, states in expected.items():
        assert _get_widget_states(result, name) == states
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
        check, check_2 = _get_field(pdf, "check"), _get_field(pdf, "check_2")
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
        stream = _save(pdf)

    prefix = "group." if shape == "kids" and use_full_widget_name else ""
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    for name in ("check", "check_2"):
        assert isinstance(obj.widgets[prefix + name], Radio)
        assert obj.widgets[prefix + name].number_of_options == 1
    assert obj.widgets[prefix + "check"].value == (0 if selected else None)

    obj.fill({prefix + "check_2": 0})
    result = obj.read()
    # the widget gets the value, and the other field keeps its own
    assert _get_widget_states(result, "check_2") == [["/Yes", "/Yes"]]
    assert _get_widget_states(result, "check") == [
        ["/Yes", "/Yes"] if selected else ["/Off", None]
    ]
    if shape == "kids":
        assert "/V" not in _find_widget(result, "check")["/Parent"].get_object()
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
        radio = _get_field(pdf, "radio_1")
        radio.Kids = Array([radio.Kids[1 - unlisted]])
        stream = _save(pdf)

    obj = PdfWrapper(stream)
    assert obj.widgets["radio_1"].number_of_options == 2

    # switching the selection selects the option and clears the other one,
    # whichever of them the field lists
    for index in indices:
        obj.fill({"radio_1": index})
        result = obj.read()
        expected = [["/Off", None], ["/Off", None]]
        expected[index][0] = f"/{index}"
        assert _get_widget_states(result, "radio_1") == expected
        assert _find_widget(result, "radio_1")["/Parent"].get_object()["/V"] == (
            f"/{index}"
        )
        assert PdfWrapper(result).data["radio_1"] == index
        assert_widgets_match_output(obj)


def test_field_below_widget_inherits_nothing_from_it(
    template_stream, assert_widgets_match_output
):
    # "test_2" gets the /Parent "test", a text field merged with its widget
    with Pdf.open(BytesIO(template_stream)) as pdf:
        test, test_2 = _get_field(pdf, "test"), _get_field(pdf, "test_2")
        test_2.Parent = test
        test.Q = 2
        test.MaxLen = 5
        test.Ff = READ_ONLY
        test.DA = String("/Cour 20 Tf 1 0 0 rg")
        del test_2["/DA"]
        pdf.Root.AcroForm.DA = String("/Helv 9 Tf 0 g")
        stream = _save(pdf)

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
    assert _find_widget(output, "test_2")["/Q"] == 1
    assert _find_widget(output, "test_2")["/DA"] == "/Helv 12 Tf 0 g"
    assert _find_widget(output, "test")["/Q"] == 2
    assert _find_widget(output, "test")["/DA"] == "/Cour 20 Tf 1 0 0 rg"
    assert_widgets_match_output(obj)


def _with_fields_above(stream, entries, holder):
    # the checked widget of "check", which keeps its name but has no /FT or /V
    # of its own, becomes a kid of the button field "group", with the entries,
    # below the field "outer", and neither field is a widget; the parent or
    # grandparent has the value /Yes, or "outer" is the parent of "group" too
    with Pdf.open(BytesIO(stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        check = _get_field(pdf, "check")
        group = pdf.make_indirect(
            Dictionary(
                {
                    "/T": String("group"),
                    "/FT": Name.Btn,
                    **entries,
                    "/Kids": Array([check]),
                }
            )
        )
        outer = pdf.make_indirect(
            Dictionary({"/T": String("outer"), "/Kids": Array([group])})
        )
        group.Parent = outer
        check.Parent = group
        check.AS = Name.Yes
        del check["/FT"]
        if holder == "cycle":
            outer.Parent = group
        else:
            {"parent": group, "grandparent": outer}[holder].V = Name.Yes
        pdf.Root.AcroForm.Fields = Array(
            [field for field in fields if field != check] + [outer]
        )
        return _save(pdf)


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
    stream = _with_fields_above(template_stream, {"/DV": Name.Yes}, holder)

    # the value is inherited through the field hierarchy
    key = "outer.group.check" if use_full_widget_name else "check"
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert type(obj.widgets[key]) is Checkbox
    assert obj.data[key] is value

    # a value of its own takes precedence
    obj.fill({key: not value})
    result = obj.read()
    state = "/Off" if value else "/Yes"
    assert _get_widget_states(result, "check") == [[state, state]]
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
    stream = _with_fields_above(template_stream, {"/Ff": RADIO}, holder)

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
    assert _get_widget_states(result, "check") == [["/Yes", "/Yes"]]
    group = _find_widget(result, "check")["/Parent"].get_object()
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
        radio = _get_field(pdf, "radio_1")
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
        stream = _save(pdf)

    key = "outer.radio_1" if use_full_widget_name else "radio_1"
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert obj.data[key] == 1

    # selecting another option writes the group's own value
    obj.fill({key: 0})
    result = obj.read()
    assert _get_widget_states(result, "radio_1") == [["/0", None], ["/Off", None]]
    radio = _find_widget(result, "radio_1")["/Parent"].get_object()
    assert radio["/V"] == "/0"
    assert radio["/Parent"].get_object()["/V"] == "/1"
    assert PdfWrapper(result, use_full_widget_name=use_full_widget_name).data[key] == 0
    assert_widgets_match_output(obj)


def test_null_checkbox_value(template_stream):
    # a null value is absent, so the checkbox isn't checked
    stream = _set_null_entries(template_stream, {"check": ["/V"]})
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
    stream = _nest_fields(template_stream, values, "/V")
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
    entries = _get_nested_entries(obj.read(), "/V")
    assert entries["test"] == "filled"
    assert entries["inner"] == values.get("inner")
    assert entries["outer"] == values["outer"]
    assert obj.widgets[other].value == values.get("inner", values["outer"])
    assert_widgets_match_output(obj)


def test_inherited_text_value_null_and_cycle(template_stream):
    # a null value is absent, so the value above it is read
    stream = _set_null_entries(
        _nest_fields(template_stream, {"outer": "outer value"}, "/V"), {"test": ["/V"]}
    )
    assert PdfWrapper(stream).widgets["test"].value == "outer value"

    # a cycle before any value reads as no value
    obj = PdfWrapper(_with_parent_cycle(template_stream, "test"))
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
    stream = _put_under_outer(sample_template_with_dropdown, ("dropdown_1",), entries)
    obj = PdfWrapper(stream)
    assert obj.widgets["dropdown_1"].value == expected

    obj.fill({"dropdown_1": 2})
    field = _find_widget(obj.read(), "dropdown_1")
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
    stream = _put_under_outer(
        sample_template_with_dropdown, ("dropdown_1",), {"/Opt": Array(["a", "b"])}
    )
    with Pdf.open(BytesIO(stream)) as pdf:
        field = _get_field(pdf, "outer").Kids[0]
        if holder == "own":
            field.Opt = Array(["x", "y"])
        elif holder in ("kid", "widget"):
            (widget,) = _split_widgets(pdf, field)
            if holder == "widget":
                widget.Opt = Array(["w"])
        stream = _save(pdf)

    obj = PdfWrapper(stream)
    assert obj.widgets["dropdown_1"].choices == expected

    # new options replace the ones found on the widget or its field, or go
    # to its field, so its other widgets get them, and "outer" keeps its own
    obj.widgets["dropdown_1"].choices = ["new"]
    annot = _find_widget(obj.read(), "dropdown_1")
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
    stream = _put_under_outer(
        sample_template_with_dropdown, ("dropdown_1",), {"/Opt": Array(["a", "b"])}
    )
    # a null /Opt is absent, so the options above it are read
    null = _set_null_entries(stream, {"dropdown_1": ["/Opt"]})
    assert PdfWrapper(null).widgets["dropdown_1"].choices == ("a", "b")

    # options that aren't an array are no options
    with Pdf.open(BytesIO(stream)) as pdf:
        _get_field(pdf, "outer").Kids[0].Opt = Name("/foo")
        malformed = _save(pdf)
    assert PdfWrapper(malformed).widgets["dropdown_1"].choices == ()

    # a cycle before any options reads as none, and changing them raises
    with Pdf.open(BytesIO(sample_template_with_dropdown)) as pdf:
        field = _get_field(pdf, "dropdown_1")
        del field["/Opt"]
        parent = pdf.make_indirect(Dictionary({"/Kids": Array([field])}))
        parent.Parent = parent
        field.Parent = parent
        cycle = _save(pdf)
    obj = PdfWrapper(cycle)
    original = obj.read()
    assert obj.widgets["dropdown_1"].choices == ()
    obj.widgets["dropdown_1"].choices = ["new"]

    with pytest.raises(ValueError, match="the /Parent chain of the field has a cycle"):
        obj.read()
    assert obj.widgets["dropdown_1"].choices == ()
    assert obj.read() == original


# a text field property, its entry, and values for it: the one chosen by the
# lookup, another one, and the one it is changed to
TEXT_FIELD_ENTRIES = [
    ("alignment", "/Q", 1, 2, 0),
    ("max_length", "/MaxLen", 3, 7, 5),
]


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
    stream = _nest_fields(template_stream, values, entry)
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
    assert _get_nested_entries(result, entry) == {
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
        stream = _save(pdf)

    obj = PdfWrapper(stream)
    assert getattr(obj.widgets["Date mois"], name) == (
        None if holder == "none" else chosen
    )
    setattr(obj.widgets["Date mois"], name, new)
    widget = _find_widget(obj.read(), "Date mois")

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
    obj = PdfWrapper(_with_parent_cycle(template_stream, "test"))
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
        _get_field(pdf, "test")[entry] = chosen
        obj = PdfWrapper(_save(pdf))
    assert getattr(obj.widgets["test"], name) == chosen
    setattr(obj.widgets["test"], name, new)

    assert _find_widget(obj.read(), "test")[entry] == new


def test_clear_alignment_below_unnamed_parent_cycle(template_stream):
    # "test" loses its name, and its parent, which has none, is its own parent
    with Pdf.open(BytesIO(template_stream)) as pdf:
        field = _get_field(pdf, "test")
        parent = pdf.make_indirect(Dictionary({"/Kids": Array([field])}))
        parent.Parent = parent
        field.Parent = parent
        field.Q = 1
        del field["/T"]
        stream = _save(pdf)

    # with full names, the widget's key is empty
    obj = PdfWrapper(stream, use_full_widget_name=True)
    original = obj.read()
    assert obj.widgets[""].alignment == 1
    obj.widgets[""].alignment = None

    with pytest.raises(ValueError, match="Cannot remove /Q: the /Parent chain"):
        obj.read()

    assert obj.widgets[""].alignment == 1
    assert obj.read() == original


def _below_unnamed_field(stream, entry, value):
    # "test" and "test_2" are kids of "outer", which sets the entry, and "test"
    # loses its name and gets an unnamed field between it and "outer"
    stream = _put_under_outer(stream, ("test", "test_2"), {entry: value})
    with Pdf.open(BytesIO(stream)) as pdf:
        outer = _get_field(pdf, "outer")
        test = outer.Kids[0]
        unnamed = pdf.make_indirect(
            Dictionary({"/FT": Name.Tx, "/Kids": Array([test]), "/Parent": outer})
        )
        outer.Kids[0] = unnamed
        test.Parent = unnamed
        del test["/T"]

        return _save(pdf)


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
    stream = _below_unnamed_field(template_stream, entry, shared)
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
        outer = _get_field(pdf, "outer")
        assert entry in outer.Kids[0]
        assert outer[entry] == _pdf_value(shared)


@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_clear_entry_below_unnamed_field(template_stream, use_full_widget_name):
    key = "" if use_full_widget_name else None
    # "outer", shared with "test_2", sets the alignment, which can't be removed
    stream = _below_unnamed_field(template_stream, "/Q", 2)
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    original = obj.read()
    obj.widgets[key].alignment = None
    with pytest.raises(ValueError, match="Cannot remove /Q: a parent field"):
        obj.read()
    assert obj.read() == original

    # the unnamed field's own tooltip is removed, and "outer" keeps its own
    stream = _below_unnamed_field(template_stream, "/TU", "outer tooltip")
    with Pdf.open(BytesIO(stream)) as pdf:
        _get_field(pdf, "outer").Kids[0].TU = String("own tooltip")
        stream = _save(pdf)
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert obj.widgets[key].tooltip == "own tooltip"
    obj.widgets[key].tooltip = None
    with Pdf.open(BytesIO(obj.read())) as pdf:
        outer = _get_field(pdf, "outer")
        assert "/TU" not in outer.Kids[0]
        assert outer.TU == "outer tooltip"


@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_change_choices_below_unnamed_field(
    sample_template_with_dropdown, use_full_widget_name
):
    # "dropdown_1" becomes an unnamed field with an unnamed widget, below
    # "outer", whose options "sibling" shares
    with Pdf.open(BytesIO(sample_template_with_dropdown)) as pdf:
        field = _get_field(pdf, "dropdown_1")
        sibling = pdf.make_indirect(Dictionary(field))
        sibling.T = String("sibling")
        del sibling["/Opt"]
        pdf.pages[0].Annots.append(sibling)
        _split_widgets(pdf, field)
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
        stream = _save(pdf)

    key, other = ("", "outer.sibling") if use_full_widget_name else (None, "sibling")
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    assert obj.widgets[key].choices == obj.widgets[other].choices == ("shared",)

    obj.widgets[key].choices = ["new"]
    reopened = PdfWrapper(obj.read(), use_full_widget_name=use_full_widget_name)
    assert reopened.widgets[key].choices == ("new",)
    assert reopened.widgets[other].choices == ("shared",)


def _with_named_parent_cycle(stream, shape):
    # "test" is moved under a field "a" whose /Parent chain loops back
    with Pdf.open(BytesIO(stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        index = next(
            i for i, each in enumerate(fields) if str(each.get("/T")) == "test"
        )
        field = fields[index]
        a = pdf.make_indirect(Dictionary({"/T": String("a"), "/Kids": Array([field])}))
        b = pdf.make_indirect(Dictionary({"/T": String("b"), "/Kids": Array([a])}))
        b.Parent = a
        # "a"'s parent is "b", or the field itself
        a.Parent = field if shape == "field" else b
        if shape in ("unnamed", "listed", "root"):
            del field["/T"]
        if shape == "listed":
            # the AcroForm lists the field instead of its widget
            fields[index] = a
        if shape == "root":
            # the AcroForm lists "b", whose /Parent "a" is its only kid
            fields[index] = b
        field.Parent = a

        return _save(pdf)


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
    stream = _with_named_parent_cycle(template_stream, shape)
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


def _with_field_cycle(stream, shape):
    # "test" and "test_2" are in a /Parent cycle
    with Pdf.open(BytesIO(stream)) as pdf:
        test, test_2 = _get_field(pdf, "test"), _get_field(pdf, "test_2")
        if shape == "group":
            # they are under "group", whose /Parent is "test"
            others = [
                each
                for each in pdf.Root.AcroForm.Fields
                if str(each.get("/T")) not in ("test", "test_2")
            ]
            group = pdf.make_indirect(
                Dictionary({"/T": String("group"), "/Kids": Array([test, test_2])})
            )
            test.Parent = group
            test_2.Parent = group
            group.Parent = test
            pdf.Root.AcroForm.Fields = Array([group, *others])
        elif shape == "three":
            # "test", "test_2", and "test_3" are each the next one's child, as
            # the /Kids also say
            test_3 = _get_field(pdf, "test_3")
            test.Parent = test_2
            test_2.Parent = test_3
            test_3.Parent = test
            test_2.Kids = Array([test])
            test_3.Kids = Array([test_2])
            test.Kids = Array([test_3])
        else:
            # each is the other's parent, and both are still listed
            test.Parent = test_2
            test_2.Parent = test
        if shape == "listing":
            # each also lists the other as a kid
            test.Kids = Array([test_2])
            test_2.Kids = Array([test])

        return _save(pdf)


@pytest.mark.parametrize("shape", ["group", "mutual", "listing", "three"])
@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_remove_fields_in_parent_cycle(
    template_stream, shape, use_full_widget_name, assert_widgets_match_output
):
    obj = PdfWrapper(
        _with_field_cycle(template_stream, shape),
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
        first_field, second_field = _get_field(pdf, "first"), _get_field(pdf, "second")
        first_field.Parent = second_field
        second_field.Parent = first_field
        if listing:
            first_field.Kids = Array([second_field])
            second_field.Kids = Array([first_field])
        stream = _save(pdf)

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
        _with_field_cycle(template_stream, shape),
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


def _with_radio_group_in_parent_cycle(stream, group, other):
    # the widgets of "check" (page 1) and "check_2" (page 2) become the
    # options of a radio group "a" with these entries, and "a" and "b", which
    # has the other entries, are each other's parent
    with Pdf.open(BytesIO(stream)) as pdf:
        options = [_get_field(pdf, "check"), _get_field(pdf, "check_2")]
        radio = pdf.make_indirect(
            Dictionary(
                {
                    "/T": String("a"),
                    "/FT": Name.Btn,
                    "/Ff": RADIO,
                    "/Kids": Array(options),
                    **group,
                }
            )
        )
        parent = pdf.make_indirect(
            Dictionary({"/T": String("b"), "/Kids": Array([radio]), **other})
        )
        radio.Parent = parent
        parent.Parent = radio
        for index, option in enumerate(options):
            del option.T
            del option.FT
            option.Parent = radio
            option.AP = Dictionary(
                N=Dictionary({"/Off": option.AP.N.Off, f"/{index}": option.AP.N.Yes})
            )
            option.AS = Name(f"/{index}") if index else Name.Off
        pdf.Root.AcroForm.Fields = Array(
            [
                each
                for each in pdf.Root.AcroForm.Fields
                if str(each.get("/T")) not in ("check", "check_2")
            ]
            + [parent]
        )

        return _save(pdf)


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
    obj = PdfWrapper(_with_radio_group_in_parent_cycle(template_stream, group, other))
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
        BytesIO(_group_fields(template_stream, ("test", "test_2"), "/Ff", 0))
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
    widget = _find_widget(obj.read(), "test")

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
    stream = _group_fields(template_stream, ("test", "test_2"), entry, parent)
    if own is not None:
        with Pdf.open(BytesIO(stream)) as pdf:
            group = _get_field(pdf, "group")
            next(kid for kid in group.Kids if str(kid.T) == "test")[entry] = own
            stream = _save(pdf)

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
    stream = _group_fields(template_stream, ("test", "test_2"), entry, Name("/invalid"))
    obj = PdfWrapper(stream)
    obj.widgets["test"].alignment = 2
    obj.read()

    # the shared parent's value is malformed, so it doesn't give the field one
    setattr(obj.widgets["test"], name, None)
    result = obj.read()

    assert _find_widget(result, "test")["/Parent"].get_object()[entry] == "/invalid"
    assert getattr(PdfWrapper(result).widgets["test"], name) is None
    assert_widgets_match_output(obj)


def _with_null_named_widget(stream):
    # "test" becomes a field with a value and a tooltip, and two widgets: the
    # first without a name, and the second with a null one, which ISO 32000-1
    # treats as absent
    widget_entries = ("/Type", "/Subtype", "/Rect", "/F", "/P", "/MK")
    with Pdf.open(BytesIO(stream)) as pdf:
        field = _get_field(pdf, "test")
        kids = []
        for name in (None, "null"):
            widget = pdf.make_indirect(
                Dictionary({key: field[key] for key in widget_entries if key in field})
            )
            widget.Parent = field
            if name is not None:
                # replaced with null below, since pikepdf removes null entries
                widget.T = String(name)
            kids.append(widget)
        for key in widget_entries:
            if key in field:
                del field[key]
        field.Kids = Array(kids)
        field.V = String("value")
        field.TU = String("tooltip")
        page = pdf.pages[0]
        page.Annots = Array(
            [
                kids[0] if annot.objgen == field.objgen else annot
                for annot in page.Annots
            ]
            + [kids[1]]
        )
        stream = _save(pdf)

    writer = PdfWriter(BytesIO(stream))
    for annot in writer.pages[0]["/Annots"]:
        annot = annot.get_object()
        if annot.get("/T") == "null":
            annot[NameObject("/T")] = NullObject()
    with BytesIO() as f:
        writer.write(f)
        return f.getvalue()


def _get_field_and_widgets(stream, name):
    # a field that has widget kids, and its kids, by the field's name
    reader = PdfReader(BytesIO(stream))
    field = next(
        each.get_object()
        for each in reader.root_object["/AcroForm"]["/Fields"]
        if each.get_object().get("/T") == name
    )
    return field, [kid.get_object() for kid in field["/Kids"]]


@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_widget_with_null_name_belongs_to_its_field(
    template_stream, use_full_widget_name, assert_widgets_match_output
):
    obj = PdfWrapper(
        _with_null_named_widget(template_stream),
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
    field, widgets = _get_field_and_widgets(obj.read(), "test")

    # changes go to the field, not to a widget
    assert (field["/Q"], field["/MaxLen"], field["/V"]) == (2, 9, "new")
    assert "/TU" not in field
    for widget in widgets:
        assert not {"/Q", "/MaxLen", "/V", "/TU"} & set(widget)
    assert_widgets_match_output(obj)


def test_rename_field_with_null_named_widget(template_stream):
    obj = PdfWrapper(_with_null_named_widget(template_stream))
    # renamed through the second widget, whose name is null
    obj.update_widget_key("test", "renamed", 1)
    obj.commit_widget_key_updates()
    _, widgets = _get_field_and_widgets(obj.read(), "renamed")

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
        stream = _save(pdf)

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
        stream = _save(pdf)

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
        stream = _save(pdf)

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


@pytest.mark.parametrize("rebuild", [False, True], ids=["same", "rebuilt"])
@pytest.mark.parametrize("separate", [False, True], ids=["merged", "separate"])
def test_fill_checkbox_with_own_on_state_again(template_stream, separate, rebuild):
    # "check" is unchecked, and its on state is /Custom rather than /Yes; with
    # separate, its widget is the kid of a field whose /DV is /Off
    with Pdf.open(BytesIO(template_stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        check = _get_field(pdf, "check")
        _set_on_state(check)
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
        stream = _save(pdf)

    obj = PdfWrapper(stream)
    obj.fill({"check": True})
    widget = _find_widget(obj.read(), "check")
    assert (widget["/AS"], widget["/V"]) == ("/Custom", "/Custom")
    # it is still a checkbox when the PDF is read again
    reopened = PdfWrapper(obj.read()).widgets["check"]
    assert type(reopened) is Checkbox
    assert reopened.value is True

    # the checked state doesn't stop the checkbox from being filled again
    if rebuild:
        obj.remove_fields(["absent"])
    obj.fill({"check": False})
    widget = _find_widget(obj.read(), "check")
    assert (widget["/AS"], widget["/V"]) == ("/Off", "/Off")
    assert obj.widgets["check"].value is False


@pytest.mark.parametrize("state", ["/Standby", "/Off"])
def test_pushbutton_is_not_a_checkbox(template_stream, state):
    # "check" becomes the pushbutton "action", which has appearance states but
    # no value
    with Pdf.open(BytesIO(template_stream)) as pdf:
        action = _get_field(pdf, "check")
        action.T = String("action")
        action.Ff = PUSHBUTTON
        action.AP = Dictionary(
            N=Dictionary({"/Activate": action.AP.N.Yes, "/Standby": action.AP.N.Off})
        )
        action.AS = Name(state)
        for entry in ("/V", "/DV"):
            if entry in action:
                del action[entry]
        stream = _save(pdf)

    obj = PdfWrapper(stream)
    assert "action" not in obj.widgets

    # filling leaves it unchanged
    widget = _find_widget(obj.fill({"action": True}).read(), "action")
    assert widget["/AS"] == state
    assert "/V" not in widget


@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_unnamed_pushbutton_with_empty_parent(template_stream, use_full_widget_name):
    # "check" becomes a pushbutton without a name, whose parent is empty, so
    # its own flags decide
    with Pdf.open(BytesIO(template_stream)) as pdf:
        check = _get_field(pdf, "check")
        check.Ff = PUSHBUTTON
        check.Parent = pdf.make_indirect(Dictionary())
        # replaced with null below, since pikepdf removes null entries
        check.T = String("null")
        if "/V" in check:
            del check["/V"]
        stream = _save(pdf)
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


def _checkbox_field(stream, states, value):
    # the widgets of "check", and of "check_2" with two states, become kids of
    # a field "check" with the value, and none has a value of its own; a widget
    # is on when the value names its state
    with Pdf.open(BytesIO(stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        names = ["check", "check_2"][: len(states)]
        kids = [_get_field(pdf, name) for name in names]
        field = pdf.make_indirect(
            Dictionary(
                {
                    "/T": String("check"),
                    "/FT": Name.Btn,
                    "/Ff": 0,
                    "/DV": Name.Off,
                    "/V": Name(value),
                    "/Kids": Array(kids),
                }
            )
        )
        for kid, state in zip(kids, states, strict=True):
            for entry in ("/T", "/FT", "/Ff", "/V"):
                if entry in kid:
                    del kid[entry]
            kid.Parent = field
            _set_on_state(kid, state)
            kid.AS = Name(state) if state == value else Name.Off
        pdf.Root.AcroForm.Fields = Array(
            [each for each in fields if each not in kids] + [field]
        )
        return _save(pdf)


def _get_checkbox_field_states(stream):
    # the /AS and /V of each widget of the field "check", and the field's /V
    field = _find_widget(stream, "check")["/Parent"].get_object()
    return _get_widget_states(stream, "check") + [field.get("/V")]


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
    stream = _checkbox_field(template_stream, states, value)

    # the field's value counts for a widget whose state it names, here the
    # last one, which "check" gives access to
    obj = PdfWrapper(stream)
    assert type(obj.widgets["check"]) is Checkbox
    assert obj.data["check"] is expected


def test_fill_keeps_checkboxes_not_supplied(template_stream, pdf_samples):
    # "check" reads True from the field's value, which names its last widget's
    # state, while its first widget is off
    stream = _checkbox_field(template_stream, ["/A", "/B"], "/B")
    obj = PdfWrapper(stream)
    assert obj.widgets["check"].value is True
    expected = [["/Off", None], ["/B", None], "/B"]

    # a value that wasn't supplied and is still the one read isn't written
    assert _get_checkbox_field_states(obj.fill({}).read()) == expected
    assert _get_checkbox_field_states(obj.fill({"test": "foo"}).read()) == expected

    # one that was assigned since is
    obj.widgets["check"].value = False
    assert _get_checkbox_field_states(obj.fill({}).read()) == [
        ["/Off", "/Off"],
        ["/Off", "/Off"],
        "/B",
    ]

    # two checkboxes are named "c1_3[1]"; the later, checked one gives the
    # name its value, and the other stays unchecked
    path = os.path.join(pdf_samples, "scenario", "issues", "PPF-939_expected_2.pdf")
    with open(path, "rb") as f:
        sample = f.read()
    filled = PdfWrapper(sample).fill({}).read()
    for stream in (sample, filled):
        assert _get_widget_states(stream, "c1_3[1]") == [["/Off", "/Off"], ["/5", "/5"]]


def test_fill_checkbox_back_to_value_read(template_stream):
    # "check" is checked
    with Pdf.open(BytesIO(template_stream)) as pdf:
        check = _get_field(pdf, "check")
        check.AS = Name.Yes
        check.V = Name.Yes
        stream = _save(pdf)

    obj = PdfWrapper(stream)
    obj.fill({"check": False})
    widget = _find_widget(obj.read(), "check")
    assert (widget["/AS"], widget["/V"]) == ("/Off", "/Off")

    # the value read is assigned again after the PDF changed, so it is written
    obj.widgets["check"].value = True
    obj.fill({})
    widget = _find_widget(obj.read(), "check")
    assert (widget["/AS"], widget["/V"]) == ("/Yes", "/Yes")


def _name_checkbox_like_radio_group(
    stream,
    position,
    radio_flag_on="field",
    checkbox_state=None,
    selected=None,
    radio_name="group",
):
    # the checkbox "check" and the radio group "outer.group" both get the short
    # name "group", unless the radio group is given another, and the radio
    # group's /DV is /Off; with a checkbox_state, the checkbox's on state is
    # /Custom, and its /AS and /V are checkbox_state, or absent if it is empty,
    # which makes it match no widget type
    with Pdf.open(BytesIO(stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        check = _get_field(pdf, "check")
        radio = _get_field(pdf, "radio_1")
        check.T = String("group")
        radio.T = String(radio_name)
        if checkbox_state is not None:
            _set_on_state(check)
            check.Ff = 0
            for entry in ("/AS", "/V"):
                if checkbox_state:
                    check[entry] = Name(checkbox_state)
                elif entry in check:
                    del check[entry]
        outer = pdf.make_indirect(
            Dictionary({"/T": String("outer"), "/Kids": Array([radio])})
        )
        radio.Parent = outer
        if radio_flag_on == "outer":
            outer.Ff = RADIO
            del radio["/Ff"]
        radio.DV = Name.Off
        if selected is not None:
            radio.V = Name(f"/{selected}")
            radio.Kids[selected].AS = Name(f"/{selected}")
        pdf.Root.AcroForm.Fields = Array(
            [field for field in fields if field != radio] + [outer]
        )
        # the checkbox comes before, between, or after the radio group's options
        options = list(radio.Kids)
        others = [
            annot
            for annot in pdf.pages[0].Annots
            if annot != check and annot not in options
        ]
        pdf.pages[0].Annots = Array(
            {
                "first": [check, *options],
                "between": [options[0], check, options[1]],
                "last": [*options, check],
            }[position]
            + others
        )
        return _save(pdf)


def _get_checkbox_and_radio_states(stream):
    # the /AS and /V of the checkbox "group", and the /AS of each option and
    # the /V of the radio group "outer.group"
    states = {"outer.group": []}
    for annot in PdfReader(BytesIO(stream)).pages[0]["/Annots"]:
        annot = annot.get_object()
        if annot.get("/T") == "group":
            states["group"] = [annot.get("/AS"), annot.get("/V")]
        elif annot.get("/Parent", {}).get("/T") == "group":
            states["outer.group"].append(annot.get("/AS"))
            states["outer.group /V"] = annot["/Parent"].get("/V")

    return states


@pytest.mark.parametrize("radio_flag_on", ["outer", "field"])
@pytest.mark.parametrize("position", ["first", "between", "last"])
def test_radio_group_with_short_name_of_another_field(
    template_with_radiobutton_stream, radio_flag_on, position
):
    stream = _name_checkbox_like_radio_group(
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
        assert _get_checkbox_and_radio_states(filled) == (
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
    stream = _name_checkbox_like_radio_group(
        template_with_radiobutton_stream, "first", checkbox_state=checkbox_state
    )
    obj = PdfWrapper(stream)
    assert obj.widgets["group"].number_of_options == 2

    # it doesn't take an option index from the radio group
    state = checkbox_state or None
    assert _get_checkbox_and_radio_states(obj.fill({"group": 0}).read()) == {
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
        other = _get_field(pdf, "check_2")
        other.T = String("check")
        _set_on_state(other)
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
        stream = _save(pdf)

    obj = PdfWrapper(stream)
    assert type(obj.widgets["check"]) is Checkbox
    filled = obj.fill({"check": False}).read()

    # filling the name changes both, as before; "outer.check" is on page 2
    assert _get_widget_states(filled, "check") == [["/Off", "/Off"], ["/Off", "/Off"]]


def test_fill_checkbox_with_short_name_of_pushbutton(template_stream):
    # the widget of "test" becomes the only widget of the pushbutton
    # "outer.action", which comes before the checkbox "check", renamed "action"
    with Pdf.open(BytesIO(template_stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        widget = _get_field(pdf, "test")
        check = _get_field(pdf, "check")
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
        stream = _save(pdf)

    obj = PdfWrapper(stream)
    assert type(obj.widgets["action"]) is Checkbox
    filled = obj.fill({"action": True}).read()

    # the pushbutton keeps having no value
    assert _get_widget_states(filled, "action") == [["/Off", None], ["/Yes", "/Yes"]]


@pytest.mark.parametrize("operation", ["rebuild", "copy"])
def test_fill_checkbox_with_short_name_of_radio_group_again(
    template_with_radiobutton_stream, operation
):
    # the unchecked checkbox comes last, and the radio group's second option
    # is selected
    stream = _name_checkbox_like_radio_group(
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

    assert _get_checkbox_and_radio_states(obj.fill({"group": False}).read()) == {
        "group": ["/Off", "/Off"],
        "outer.group": ["/Off", "/1"],
        "outer.group /V": "/1",
    }


def test_fill_checkbox_after_rename_gives_radio_group_its_name(
    template_with_radiobutton_stream,
):
    # the radio group "outer.radio" comes before the checkbox "group"
    stream = _name_checkbox_like_radio_group(
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
    assert _get_checkbox_and_radio_states(obj.fill({"group": True}).read()) == expected
    filled = PdfWrapper(renamed).fill({"group": True}).read()
    assert _get_checkbox_and_radio_states(filled) == expected
