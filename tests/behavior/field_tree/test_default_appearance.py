# -*- coding: utf-8 -*-

import decimal
from io import BytesIO

import pytest
from pikepdf import Dictionary, Name, Object, Pdf, String
from pypdf import PdfReader

from PyPDFForm import PdfWrapper
from PyPDFForm.lib import wrapper
from tests.support.builders import (
    CHOSEN_DA,
    OTHER_DA,
    get_field,
    nest_fields,
    save,
    set_default_appearance,
    split_widgets,
    with_null_default_appearance,
    with_parent_cycle,
)
from tests.support.checks import find_widget, get_nested_entries


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
    stream = nest_fields(template_stream, default_appearances)
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)
    widget = obj.widgets["outer.inner.test" if use_full_widget_name else "test"]
    # the /DA that the change edits is the one read
    assert (widget.font, widget.font_size, widget.font_color) == ("/Cour", 9, (0, 0, 1))

    setattr(widget, name, value)
    result = get_nested_entries(obj.read())

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
    appearance = find_widget(filled.read(), "test")["/AP"]["/N"].get_data()
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
            stream = save(pdf)

    obj = PdfWrapper(stream)
    obj.widgets["Date mois"].font_size = 20
    widget = find_widget(obj.read(), "Date mois")

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
        stream = save(pdf)

    obj = PdfWrapper(stream)
    widget = obj.widgets["dropdown_1"]
    assert (widget.font, widget.font_size, widget.font_color) == ("/Helv", 0, (0, 0, 0))
    widget.font_size = 20
    widget.font_color = (1, 0, 0)

    assert find_widget(obj.read(), "dropdown_1")["/DA"] == "/Helv 20 Tf 1 0 0 rg"
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
        set_default_appearance(template_stream, "test", default_appearance)
    )
    setattr(obj.widgets["test"], name, value)

    assert find_widget(obj.read(), "test")["/DA"] == expected


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
        with_parent_cycle(template_stream, "test")
        if default_appearance is None
        else set_default_appearance(template_stream, "test", default_appearance)
    )
    widget = PdfWrapper(stream).widgets["test"]

    assert (widget.font, widget.font_size, widget.font_color) == expected


def test_default_appearance_in_any_decimal_context(template_stream):
    stream = set_default_appearance(
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
            find_widget(obj.read(), "test")["/DA"]
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
        with_parent_cycle(template_stream, "test")
        if default_appearance is None
        else set_default_appearance(template_stream, "test", default_appearance)
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

    assert find_widget(obj.read(), "test")["/DA"] == "/Arial 12 Tf 0 0 1 rg"


def test_change_default_appearance_over_null(template_stream):
    # a null /DA is absent, so the AcroForm default is used
    obj = PdfWrapper(with_null_default_appearance(template_stream, False))
    widget = obj.widgets["test"]
    assert (widget.font, widget.font_size, widget.font_color) == ("/Helv", 0, (0, 0, 0))
    widget.font_size = 14

    assert find_widget(obj.read(), "test")["/DA"] == "/Helv 14 Tf 0 g "

    obj = PdfWrapper(with_null_default_appearance(template_stream, True))
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
        stream = save(pdf)

    obj = PdfWrapper(stream)
    assert "Courier" in obj.fonts
    obj.widgets["test"].font = "Courier"
    default_appearance = find_widget(obj.read(), "test")["/DA"]

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
    stream = set_default_appearance(template_stream, "test", "/Helv 12 Tf 0 g")
    stream = set_default_appearance(stream, "test_2", "Courier 10 Tf 0 g")
    obj = PdfWrapper(stream).register_font("Courier", sample_font_stream)
    assert obj.widgets["test_2"].font == "Courier"

    obj.widgets["test"].font = "Courier"
    result = obj.read()
    resource = obj.widgets["test"].font

    # only the font being changed becomes the registered font's resource
    assert resource.startswith("/")
    assert find_widget(result, "test")["/DA"] == f"{resource} 12 Tf 0 g"
    assert find_widget(result, "test_2")["/DA"] == "Courier 10 Tf 0 g"
    assert obj.widgets["test_2"].font == "Courier"
    assert_widgets_match_output(obj)


def test_assign_back_font_read_without_slash(template_stream):
    stream = set_default_appearance(template_stream, "test", "Courier 12 Tf 0 g")
    obj = PdfWrapper(stream)
    assert obj.widgets["test"].font == "Courier"

    # the font the field uses is kept as it is
    obj.widgets["test"].font = obj.widgets["test"].font
    assert find_widget(obj.read(), "test")["/DA"] == "Courier 12 Tf 0 g"

    # another field doesn't use it, so it is a font the PDF doesn't have
    original = obj.read()
    obj.widgets["test_2"].font = "Courier"
    with pytest.raises(ValueError, match="'Courier' is not a registered font"):
        obj.read()
    assert obj.read() == original


def test_assign_back_font_with_name_of_registered_font(
    template_stream, sample_font_stream
):
    stream = set_default_appearance(template_stream, "test", "Helvetica 12 Tf 0 g")
    obj = PdfWrapper(stream).register_font("Helvetica", sample_font_stream)
    assert obj.widgets["test"].font == "Helvetica"

    # the font the field uses is kept, not replaced by the registered one
    obj.widgets["test"].font = obj.widgets["test"].font
    assert find_widget(obj.read(), "test")["/DA"] == "Helvetica 12 Tf 0 g"

    # another field gets the registered font
    obj.widgets["test_2"].font = "Helvetica"
    font = find_widget(obj.read(), "test_2")["/DA"].split()[0]
    assert font != "Helvetica"
    assert PdfWrapper(obj.read()).widgets["test_2"].font == font


def test_font_change_is_decided_per_annotation(
    template_stream, assert_widgets_match_output
):
    # the PDF's /Helv font has the base font Helvetica
    stream = set_default_appearance(template_stream, "test", "Helvetica 12 Tf 0 g")

    # a font changed and changed back is looked up again
    obj = PdfWrapper(stream)
    obj.widgets["test"].font = "/Arial"
    obj.widgets["test"].font = "Helvetica"
    assert find_widget(obj.read(), "test")["/DA"] == "/Helv 12 Tf 0 g"
    assert obj.widgets["test"].font == "/Helv"
    assert_widgets_match_output(obj)

    # only the widget that uses the font keeps it, and the field reads it from
    # its last widget, as reopening does
    with Pdf.open(BytesIO(template_stream)) as pdf:
        widgets = split_widgets(pdf, get_field(pdf, "test"), 2)
        for widget, default_appearance in zip(
            widgets, ("/Arial 9 Tf 0 g", "Helvetica 12 Tf 0 g"), strict=True
        ):
            widget.DA = String(default_appearance)
        obj = PdfWrapper(save(pdf))
    assert obj.widgets["test"].font == "Helvetica"
    obj.widgets["test"].font = obj.widgets["test"].font
    with Pdf.open(BytesIO(obj.read())) as pdf:
        kids = get_field(pdf, "test").Kids
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
    assert find_widget(obj.read(), "test")["/DA"].startswith("/Helv ")
    assert obj.widgets["test"].font == "/Helv"
    assert_widgets_match_output(obj)
