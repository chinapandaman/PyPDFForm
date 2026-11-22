# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from pikepdf import Array, Dictionary, Name, Object, Pdf, String
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NullObject

from PyPDFForm import Fields, PdfWrapper, RawElements
from PyPDFForm.lib.constants import COMB, MULTILINE, RADIO, READ_ONLY, REQUIRED
from PyPDFForm.lib.hooks import update_field_readonly
from PyPDFForm.lib.middleware.radio import Radio
from PyPDFForm.lib.patterns import get_widget_key
from PyPDFForm.lib.utils import get_version, set_version


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


def test_version_leaves_failing_tooltip_removal_to_read(template_stream):
    stream = _group_fields(template_stream, ("test", "test_2"), "/TU", "shared tooltip")
    # below 1.5, the version getter previews queued tooltip changes
    obj = PdfWrapper(set_version(stream, get_version(stream), "1.4"))
    widget = obj.widgets["test"]
    widget.tooltip = "own tooltip"
    obj.read()

    widget.tooltip = None
    assert obj.version == "1.4"
    assert widget.hooks_to_trigger

    with pytest.raises(ValueError, match="Cannot remove /TU"):
        obj.read()
    assert widget.tooltip == "own tooltip"


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
    setattr(
        obj.widgets["outer.inner.test" if use_full_widget_name else "test"], name, value
    )
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


def test_change_inherited_dropdown_default_appearance(sample_template_with_dropdown):
    with Pdf.open(BytesIO(sample_template_with_dropdown)) as pdf:
        for field in pdf.Root.AcroForm.Fields:
            if str(field.get("/T")) == "dropdown_1":
                del field["/DA"]
        pdf.Root.AcroForm.DA = String("/Helv 0 Tf 0 g")
        stream = _save(pdf)

    obj = PdfWrapper(stream)
    obj.widgets["dropdown_1"].font_size = 20
    obj.widgets["dropdown_1"].font_color = (1, 0, 0)

    assert _find_widget(obj.read(), "dropdown_1")["/DA"] == "/Helv 20 Tf 1 0 0 rg"
    assert (
        PdfReader(BytesIO(obj.read())).root_object["/AcroForm"]["/DA"]
        == "/Helv 0 Tf 0 g"
    )


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
    ("default_appearance", "name", "value", "message"),
    [
        ("0 g", "font_size", 20, "has no Tf operator"),
        ("0 g", "font", "/Helv", "has no Tf operator"),
        ("/Helv Tf 0 g", "font_size", 20, "needs a font and a font size"),
        ("12 Tf 0 g", "font", "/Helv", "needs a font and a font size"),
        ("/Helv /F1 Tf 0 g", "font_size", 20, "needs a font and a font size"),
        ("/Helv 12 Tf (x) Tj", "font_size", 20, r"unexpected '\('"),
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
    # applied before the failing change, and discarded with it
    obj.widgets["test"].alignment = 2
    setattr(obj.widgets["test"], name, value)

    with pytest.raises(ValueError, match=message):
        obj.read()

    assert obj.widgets["test"].alignment is None
    assert getattr(obj.widgets["test"], name) is None
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
    obj.widgets["test"].font_size = 14

    assert _find_widget(obj.read(), "test")["/DA"] == "/Helv 14 Tf 0 g "

    obj = PdfWrapper(_with_null_default_appearance(template_stream, True))
    obj.widgets["test"].font_size = 14
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
        for field in pdf.Root.AcroForm.Fields:
            if str(field.get("/T")) == "test":
                field.Ff = flag
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
        radio = next(field for field in fields if str(field.get("/T")) == "radio_1")
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


@pytest.mark.parametrize(
    ("value", "error"),
    [(String(""), ValueError), (Array([]), TypeError), (Dictionary({}), TypeError)],
    ids=["string", "array", "dictionary"],
)
def test_reject_field_flags_that_are_not_a_number(template_stream, value, error):
    with Pdf.open(BytesIO(template_stream)) as pdf:
        for field in pdf.Root.AcroForm.Fields:
            if str(field.get("/T")) == "test":
                field.Ff = value
        stream = _save(pdf)

    # they aren't read as no flags
    with pytest.raises(error):
        PdfWrapper(stream)

    # nor overwritten by a change
    widget = _find_widget(stream, "test")
    with pytest.raises(error):
        update_field_readonly(widget, True)
    assert _find_widget(stream, "test")["/Ff"] == widget["/Ff"]


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
