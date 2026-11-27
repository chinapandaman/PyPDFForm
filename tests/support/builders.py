# -*- coding: utf-8 -*-

import os
from io import BytesIO

from pikepdf import Array, Dictionary, Name, Pdf, String
from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    NullObject,
    NumberObject,
    TextStringObject,
)

from PyPDFForm.lib.constants import DA, RADIO, T
from PyPDFForm.lib.patterns import get_widget_key

# chosen by the lookup, then changed: font size 20, red, or the /Helv font
CHOSEN_DA = "/Cour 9 Tf 0 0 1 rg"
OTHER_DA = "/Helv 5 Tf 0 g"
# a flag that no property changes, which a change keeps
OTHER_FLAG = 1 << 22


# Saving and looking up fields
def save(pdf):
    with BytesIO() as f:
        pdf.save(f)
        return f.getvalue()


def get_field(pdf, name):
    # a field of the AcroForm by its name
    return next(
        field for field in pdf.Root.AcroForm.Fields if str(field.get("/T")) == name
    )


def pdf_value(value):
    return String(value) if isinstance(value, str) else value


# Versions, catalogs, and actions
def blank_pdf(version):
    writer = PdfWriter()
    writer.add_blank_page(width=360, height=360)
    writer.pdf_header = f"%PDF-{version}"
    with BytesIO() as f:
        writer.write(f)
        return f.getvalue()


def pdf_with_catalog_version(header, catalog_version, squiggly_page=None):
    writer = PdfWriter()
    writer.add_blank_page(width=360, height=360)
    writer.add_blank_page(width=360, height=360)
    writer.pdf_header = f"%PDF-{header}"
    writer.root_object[NameObject("/Version")] = catalog_version
    if squiggly_page is not None:
        writer.pages[squiggly_page - 1][NameObject("/Annots")] = ArrayObject(
            [
                writer._add_object(  # type: ignore # noqa: SLF001
                    DictionaryObject(
                        {
                            NameObject("/Type"): NameObject("/Annot"),
                            NameObject("/Subtype"): NameObject("/Squiggly"),
                            NameObject("/Rect"): ArrayObject(
                                [NumberObject(10), NumberObject(10)] * 2
                            ),
                        }
                    )
                )
            ]
        )
    with BytesIO() as f:
        writer.write(f)
        return f.getvalue()


def with_catalog_extras(stream):
    # adds fields PyPDFForm doesn't list in `widgets`: a field without a widget,
    # an unsupported push button on page 1, a parent of test_2 and test_3, and a
    # calculation order
    with Pdf.open(BytesIO(stream)) as pdf:
        acroform = pdf.Root.AcroForm
        page = pdf.pages[0].obj
        fields = {str(field.T): field for field in acroform.Fields}
        group = pdf.make_indirect(
            Dictionary(
                T=String("group"), Kids=Array([fields["test_2"], fields["test_3"]])
            )
        )
        for name in ("test_2", "test_3"):
            fields[name].Parent = group
        button = pdf.make_indirect(
            Dictionary(
                Type=Name.Annot,
                Subtype=Name.Widget,
                FT=Name.Btn,
                Ff=1 << 16,
                T=String("submit_button"),
                Rect=Array([0, 0, 20, 20]),
                P=page,
            )
        )
        page.Annots.append(button)
        hidden = pdf.make_indirect(
            Dictionary(FT=Name.Tx, T=String("hidden_business_id"), V=String("12345"))
        )
        acroform.Fields = Array(
            [
                field
                for name, field in fields.items()
                if name not in ("test_2", "test_3")
            ]
            + [group, button, hidden]
        )
        acroform.CO = Array([fields["test"], fields["test_2"], hidden])

        with BytesIO() as f:
            pdf.save(f)
            return f.getvalue()


def with_actions(stream, add):
    # calls add(pdf, fields) on the form from with_catalog_extras, where
    # fields maps the fully qualified name of each field to it
    with Pdf.open(BytesIO(with_catalog_extras(stream))) as pdf:
        fields = {str(field.T): field for field in pdf.Root.AcroForm.Fields}
        fields.update({f"group.{kid.T}": kid for kid in fields["group"].Kids})
        add(pdf, fields)

        with BytesIO() as f:
            pdf.save(f)
            return f.getvalue()


def build_action(spec, test):
    # spec is (label, following): "reset" names only test, any other label is
    # the JavaScript of the action, and following is None, a spec, or a list
    label, following = spec
    action = (
        Dictionary(S=Name.ResetForm, Fields=Array([test]))
        if label == "reset"
        else Dictionary(S=Name.JavaScript, JS=String(label))
    )
    if isinstance(following, list):
        action.Next = Array([build_action(each, test) for each in following])
    elif following is not None:
        action.Next = build_action(following, test)
    return action


# Forms across pages
def build_cross_page_form(page_action=True):
    pdf = Pdf.new()
    for _ in range(3):
        pdf.add_blank_page()
    page_1, page_2, page_3 = (page.obj for page in pdf.pages)

    def stream(data, **kwargs):
        return pdf.make_stream(data, **kwargs)

    def appearance(text):
        return stream(
            b"BT /Helv 10 Tf 2 2 Td (" + text + b") Tj ET",
            Type=Name.XObject,
            Subtype=Name.Form,
            BBox=[0, 0, 100, 20],
        )

    def annotate(page, rect, **kwargs):
        annot = pdf.make_indirect(
            Dictionary(Type=Name.Annot, Rect=rect, P=page, **kwargs)
        )
        if "/Annots" not in page:
            page.Annots = pdf.make_indirect([])
        page.Annots.append(annot)
        return annot

    def goto(page):
        return Dictionary(S=Name.GoTo, D=[page, Name.Fit])

    page_1.Contents = stream(b"BT /F1 12 Tf 30 700 Td (KEEP_PAGE_1) Tj ET")
    if page_action:
        page_1.AA = Dictionary(O=goto(page_2))
    page_2.Contents = stream(b"BT /F1 12 Tf 30 700 Td (SECRET_PAGE_2) Tj ET /Im0 Do")
    page_2.Resources = Dictionary(
        XObject=Dictionary(
            Im0=stream(
                b"SECRET_IMAGE",
                Type=Name.XObject,
                Subtype=Name.Image,
                Width=12,
                Height=1,
                ColorSpace=Name.DeviceGray,
                BitsPerComponent=8,
            )
        )
    )

    # A text field with widgets on pages 1 and 2.
    shared = pdf.make_indirect(Dictionary(FT=Name.Tx, T="shared", V="shared_value"))
    shared.Kids = [
        annotate(
            page,
            [10, 10, 110, 30],
            Subtype=Name.Widget,
            Parent=shared,
            AP=Dictionary(N=appearance(text)),
        )
        for page, text in ((page_1, b"shared_value"), (page_2, b"SECRET_SHARED_AP"))
    ]
    # A parent field whose children are on pages 1 and 2.
    person = pdf.make_indirect(Dictionary(T="person"))
    person.Kids = [
        annotate(
            page,
            [10, 50, 110, 70],
            Subtype=Name.Widget,
            FT=Name.Tx,
            T=name,
            V=value,
            Parent=person,
        )
        for page, name, value in (
            (page_1, "name", "KEEP_NAME"),
            (page_2, "address", "SECRET_ADDRESS"),
        )
    ]
    # A parent field whose only child is on page 2.
    contact = pdf.make_indirect(Dictionary(T="contact"))
    contact.Kids = [
        annotate(
            page_2,
            [10, 90, 110, 110],
            Subtype=Name.Widget,
            FT=Name.Tx,
            T="solo",
            V="SECRET_SOLO",
            Parent=contact,
        )
    ]
    # A radio group with buttons on pages 1 and 3.
    radio = pdf.make_indirect(
        Dictionary(FT=Name.Btn, Ff=49152, T="radio", V=Name("/b"))
    )
    radio.Kids = [
        annotate(
            page,
            [10, 130, 20, 140],
            Subtype=Name.Widget,
            Parent=radio,
            AS=state if selected else Name.Off,
            AP=Dictionary(N=Dictionary({state: appearance(text)})),
        )
        for page, state, text, selected in (
            (page_1, "/a", b"radio_a", False),
            (page_3, "/b", b"SECRET_RADIO_AP", True),
        )
    ]
    note = annotate(page_1, [200, 200, 220, 220], Subtype=Name.Text, Contents="note")
    note.Popup = annotate(page_1, [220, 200, 320, 260], Subtype=Name.Popup, Parent=note)
    buttons = [
        annotate(
            page_1,
            [300, y, 350, y + 20],
            Subtype=Name.Widget,
            FT=Name.Btn,
            Ff=65536,
            T=name,
            **actions,
        )
        for y, name, actions in (
            (
                10,
                "next",
                {"A": Dictionary(S=Name.GoTo, D=pdf.make_indirect([page_2, Name.Fit]))},
            ),
            (50, "last", {"AA": Dictionary(U=goto(page_3), D=goto(page_1))}),
            (90, "top", {"A": goto(page_1)}),
        )
    ]
    annotate(page_1, [400, 10, 450, 30], Subtype=Name.Link, Dest=[page_2, Name.Fit])
    pdf.Root.AcroForm = pdf.make_indirect(
        Dictionary(Fields=[shared, person, contact, radio, *buttons])
    )

    result = BytesIO()
    pdf.save(result)
    return result.getvalue()


# Default appearances
def without_default_appearance(stream, key):
    # neither the field nor the AcroForm default sets a default appearance
    writer = PdfWriter(BytesIO(stream))
    del writer.root_object["/AcroForm"][NameObject(DA)]
    for annot in writer.pages[0]["/Annots"]:
        annot = annot.get_object()
        if annot.get(T) == key:
            del annot[NameObject(DA)]

    with BytesIO() as f:
        writer.write(f)
        return f.getvalue()


def set_default_appearance(stream, name, default_appearance):
    # sets the /DA of a field whose widget has its name
    with Pdf.open(BytesIO(stream)) as pdf:
        for field in pdf.Root.AcroForm.Fields:
            if str(field.get("/T")) == name:
                field.DA = pdf_value(default_appearance)

        return save(pdf)


def with_null_default_appearance(stream, acroform_null):
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


# Field trees and null entries
def set_parent_entry(stream, name, entry, value):
    # sets the entry on the parent field of a widget without a name
    with Pdf.open(BytesIO(stream)) as pdf:
        for page in pdf.pages:
            for annot in page.get("/Annots", []):
                if "/Parent" in annot and str(annot.Parent.get("/T")) == name:
                    annot.Parent[entry] = pdf_value(value)

        with BytesIO() as f:
            pdf.save(f)
            return f.getvalue()


def set_null_entries(stream, entries):
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


def with_null_entry(stream, name, key):
    # sets an entry of the field with this name (/T), at any level, to null
    writer = PdfWriter(BytesIO(stream))
    stack = list(writer.root_object["/AcroForm"]["/Fields"])
    while stack:
        field = stack.pop().get_object()
        if field.get("/T") == name:
            field[NameObject(key)] = NullObject()
        stack.extend(field.get("/Kids", []))
    with BytesIO() as f:
        writer.write(f)
        return f.getvalue()


def group_fields(stream, names, entry, value):
    # make the fields kids of a parent field that sets the entry
    with Pdf.open(BytesIO(stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        kids = [field for field in fields if str(field.get("/T")) in names]
        parent = pdf.make_indirect(
            Dictionary(
                {
                    "/T": String("group"),
                    "/Kids": Array(kids),
                    entry: pdf_value(value),
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


def nest_fields(stream, values, entry="/DA"):
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
            holders[holder][entry] = pdf_value(value)

        return save(pdf)


def put_under_outer(stream, names, entries):
    # makes "outer" the parent of the fields with these names, in this order,
    # and moves the entries from them to "outer"
    with Pdf.open(BytesIO(stream)) as pdf:
        kids = [get_field(pdf, name) for name in names]
        outer = pdf.make_indirect(
            Dictionary({"/T": String("outer"), "/Kids": Array(kids)})
        )
        for entry, value in entries.items():
            for kid in kids:
                if entry in kid:
                    del kid[entry]
            outer[entry] = pdf_value(value)
        for kid in kids:
            kid.Parent = outer
        pdf.Root.AcroForm.Fields = Array(
            [each for each in pdf.Root.AcroForm.Fields if each not in kids] + [outer]
        )

        return save(pdf)


def split_widgets(pdf, field, count=1):
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


def with_fields_above(stream, entries, holder):
    # the checked widget of "check", which keeps its name but has no /FT or /V
    # of its own, becomes a kid of the button field "group", with the entries,
    # below the field "outer", and neither field is a widget; the parent or
    # grandparent has the value /Yes, or "outer" is the parent of "group" too
    with Pdf.open(BytesIO(stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        check = get_field(pdf, "check")
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
        return save(pdf)


def below_unnamed_field(stream, entry, value):
    # "test" and "test_2" are kids of "outer", which sets the entry, and "test"
    # loses its name and gets an unnamed field between it and "outer"
    stream = put_under_outer(stream, ("test", "test_2"), {entry: value})
    with Pdf.open(BytesIO(stream)) as pdf:
        outer = get_field(pdf, "outer")
        test = outer.Kids[0]
        unnamed = pdf.make_indirect(
            Dictionary({"/FT": Name.Tx, "/Kids": Array([test]), "/Parent": outer})
        )
        outer.Kids[0] = unnamed
        test.Parent = unnamed
        del test["/T"]

        return save(pdf)


def with_null_named_widget(stream):
    # "test" becomes a field with a value and a tooltip, and two widgets: the
    # first without a name, and the second with a null one, which ISO 32000-1
    # treats as absent
    widget_entries = ("/Type", "/Subtype", "/Rect", "/F", "/P", "/MK")
    with Pdf.open(BytesIO(stream)) as pdf:
        field = get_field(pdf, "test")
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
        stream = save(pdf)

    writer = PdfWriter(BytesIO(stream))
    for annot in writer.pages[0]["/Annots"]:
        annot = annot.get_object()
        if annot.get("/T") == "null":
            annot[NameObject("/T")] = NullObject()
    with BytesIO() as f:
        writer.write(f)
        return f.getvalue()


# Parent cycles
def with_parent_cycle(stream, name):
    # the field's /DA is removed, and its parent is its own parent
    with Pdf.open(BytesIO(stream)) as pdf:
        for field in pdf.Root.AcroForm.Fields:
            if str(field.get("/T")) == name:
                parent = pdf.make_indirect(Dictionary({"/Kids": Array([field])}))
                parent.Parent = parent
                field.Parent = parent
                del field["/DA"]

        return save(pdf)


def with_named_parent_cycle(stream, shape):
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

        return save(pdf)


def with_field_cycle(stream, shape):
    # "test" and "test_2" are in a /Parent cycle
    with Pdf.open(BytesIO(stream)) as pdf:
        test, test_2 = get_field(pdf, "test"), get_field(pdf, "test_2")
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
            test_3 = get_field(pdf, "test_3")
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

        return save(pdf)


def with_radio_group_in_parent_cycle(stream, group, other):
    # the widgets of "check" (page 1) and "check_2" (page 2) become the
    # options of a radio group "a" with these entries, and "a" and "b", which
    # has the other entries, are each other's parent
    with Pdf.open(BytesIO(stream)) as pdf:
        options = [get_field(pdf, "check"), get_field(pdf, "check_2")]
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

        return save(pdf)


# Checkboxes and radio groups
def build_button_group(field_flags, default, on_index, value=None):
    pdf = Pdf.new()
    pdf.add_blank_page()
    page = pdf.pages[0].obj
    appearance = pdf.make_stream(
        b"", Type=Name.XObject, Subtype=Name.Form, BBox=[0, 0, 10, 10]
    )
    field = pdf.make_indirect(
        Dictionary(FT=Name.Btn, Ff=field_flags, T="group", DV=default)
    )
    if value is not None:
        field.V = value
    kids = [
        pdf.make_indirect(
            Dictionary(
                Type=Name.Annot,
                Subtype=Name.Widget,
                Rect=[10 + 20 * index, 10, 20 + 20 * index, 20],
                P=page,
                Parent=field,
                AP=Dictionary(N=Dictionary({state: appearance, "/Off": appearance})),
                AS=Name(state) if index == on_index else Name.Off,
            )
        )
        for index, state in enumerate(("/a", "/b"))
    ]
    field.Kids = kids
    page.Annots = kids
    pdf.Root.AcroForm = Dictionary(Fields=[field])
    stream = BytesIO()
    pdf.save(stream)
    return stream.getvalue()


def set_on_state(widget, state="/Custom"):
    # gives a checkbox widget an on state other than /Yes
    widget.AP.N = Dictionary({"/Off": widget.AP.N.Off, state: widget.AP.N.Yes})


def with_button_parent(stream, shape):
    # "check_2" gets the /Parent "check", a button field that doesn't list it
    with Pdf.open(BytesIO(stream)) as pdf:
        check, check_2 = get_field(pdf, "check"), get_field(pdf, "check_2")
        check_2.Parent = check
        if shape == "unnamed":
            del check_2.T
        elif shape == "cycle":
            # "check" also sets the radio flag, lists "check_2" as a kid, and
            # has "check_2" as its own parent
            check.Parent = check_2
            check.Kids = Array([check_2])
            check.Ff = RADIO

        return save(pdf)


def checkbox_field(stream, states, value):
    # the widgets of "check", and of "check_2" with two states, become kids of
    # a field "check" with the value, and none has a value of its own; a widget
    # is on when the value names its state
    with Pdf.open(BytesIO(stream)) as pdf:
        fields = pdf.Root.AcroForm.Fields
        names = ["check", "check_2"][: len(states)]
        kids = [get_field(pdf, name) for name in names]
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
            set_on_state(kid, state)
            kid.AS = Name(state) if state == value else Name.Off
        pdf.Root.AcroForm.Fields = Array(
            [each for each in fields if each not in kids] + [field]
        )
        return save(pdf)


def name_checkbox_like_radio_group(
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
        check = get_field(pdf, "check")
        radio = get_field(pdf, "radio_1")
        check.T = String("group")
        radio.T = String(radio_name)
        if checkbox_state is not None:
            set_on_state(check)
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
        return save(pdf)


# CLI input files
def write_invalid_json(tmp_path, content):
    data_path = tmp_path / "invalid.json"
    data_path.write_text(content, encoding="utf-8")
    return str(data_path)


def write_invalid_yaml(tmp_path, content):
    data_path = tmp_path / "invalid.yaml"
    data_path.write_text(content, encoding="utf-8")
    return str(data_path)


# Issue reproductions
def javascript(script):
    return DictionaryObject(
        {
            NameObject("/S"): NameObject("/JavaScript"),
            NameObject("/JS"): TextStringObject(script),
        }
    )


def hide_target_form(issue_pdf_directory, edit=None):
    # saved by PyPDFForm before PPF-2100: the widgets of "shared", one per page
    # at the same rect, are inline, /Kids lists their copies in reverse page
    # order, and a Hide action targets the page 2 copy
    path = os.path.join(issue_pdf_directory, "PPF-2100-hide-target.pdf")
    if edit is None:
        return path

    writer = PdfWriter(clone_from=path)
    for page in writer.pages:
        edit(page["/Annots"][0].get_object())
    with BytesIO() as f:
        writer.write(f)
        return f.getvalue()


def set_flags(widget):
    widget[NameObject("/F")] = NumberObject(4)


def drop_page(widget):
    widget.pop("/P", None)


def drop_page_from_copies(widget):
    # the page widgets and both copies are then equal
    drop_page(widget)
    for kid in widget["/Parent"]["/Kids"]:
        drop_page(kid.get_object())
