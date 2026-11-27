# -*- coding: utf-8 -*-

from io import BytesIO

import pikepdf
import pytest

from PyPDFForm import PdfWrapper
from PyPDFForm.lib.middleware.checkbox import Checkbox


def _read_stream(obj):
    try:
        return obj.read_bytes()
    except pikepdf.PdfError:
        # stored with a filter qpdf doesn't decode, such as an image codec
        return obj.read_raw_bytes()


def describe_pdf(stream, timestamped=False):
    # the version, trailer, and objects of a PDF, described so that they don't
    # depend on how its streams are compressed
    with pikepdf.Pdf.open(BytesIO(stream)) as pdf:
        trailer = pikepdf.Dictionary(pdf.trailer)
        if "/ID" in trailer:
            # derived from the creation time or from the written bytes
            del trailer["/ID"]
        info = pdf.trailer.get("/Info")
        description = {"version": pdf.pdf_version, "trailer": trailer.unparse()}
        for index, obj in enumerate(pdf.objects):
            if not isinstance(obj, pikepdf.Object):
                # an indirect number or boolean, which has no object number here
                description[f"object at index {index}"] = repr(obj)
            elif isinstance(obj, pikepdf.Stream):
                properties = pikepdf.Dictionary(obj.stream_dict)
                # the length of the stored, usually compressed, data
                del properties["/Length"]
                description[obj.objgen] = properties.unparse(), _read_stream(obj)
            elif timestamped and info is not None and obj.objgen == info.objgen:
                dated = pikepdf.Dictionary(obj)
                for key in ("/CreationDate", "/ModDate"):
                    if key in dated:
                        del dated[key]
                description[obj.objgen] = dated.unparse()
            else:
                description[obj.objgen] = obj.unparse(resolved=True)

        return description


def assert_same_pdf(actual, expected, standard_zlib, timestamped=False):
    # for PDFs whose bytes depend on Python's zlib: the PDF must have the same
    # objects as the expected PDF on every platform, and the same bytes with
    # standard zlib
    actual_description = describe_pdf(actual, timestamped)
    expected_description = describe_pdf(expected, timestamped)
    differences = sorted(
        str(key)
        for key in actual_description.keys() | expected_description.keys()
        if actual_description.get(key) != expected_description.get(key)
    )
    assert not differences

    if standard_zlib:
        assert len(actual) == len(expected)
        if not timestamped:
            # a timestamped PDF only keeps its length between runs
            assert actual == expected


def assert_page_ownership(stream):
    # every page is in the page tree, every annotation belongs to the page that
    # lists it, and every widget of a listed field is on a page
    with pikepdf.Pdf.open(BytesIO(stream)) as pdf:
        pages = {page.obj.objgen for page in pdf.pages}
        assert not [
            obj.objgen
            for obj in pdf.objects
            if isinstance(obj, pikepdf.Dictionary)
            and obj.get("/Type") == pikepdf.Name.Page
            and obj.objgen not in pages
        ]
        annots = {}
        for page in pdf.pages:
            for annot in page.get("/Annots", []):
                annots[annot.objgen] = annot
                if "/P" in annot:
                    assert annot.P.objgen == page.obj.objgen
        for annot in annots.values():
            parent = (
                annot.get("/Parent") if annot.Subtype == pikepdf.Name.Widget else None
            )
            while parent is not None:
                assert all(
                    kid.objgen in annots or "/Kids" in kid for kid in parent.Kids
                )
                parent = parent.get("/Parent")


def assert_catalog_fields(stream, names):
    # the catalog lists exactly the fields with these fully qualified names, and
    # their widgets are exactly the widgets on the pages, each of them once; a
    # field without kids is its own widget unless it isn't a widget annotation,
    # such as a hidden field
    with pikepdf.Pdf.open(BytesIO(stream)) as pdf:
        on_pages = [
            annot.objgen
            for page in pdf.pages
            for annot in page.get("/Annots", [])
            if annot.get("/Subtype") == pikepdf.Name.Widget
        ]
        acroform = pdf.Root.get("/AcroForm", pikepdf.Dictionary())
        pending = [(field, "") for field in acroform.get("/Fields", [])]
        found = []
        listed = []
        while pending:
            field, prefix = pending.pop()
            name = prefix + str(field.get("/T", ""))
            kids = list(field.get("/Kids", []))
            # kids with a name are fields, the others are the field's widgets
            pending.extend((kid, f"{name}.") for kid in kids if "/T" in kid)
            widgets = [kid for kid in kids if "/T" not in kid]
            if not kids and field.get("/Subtype") == pikepdf.Name.Widget:
                widgets = [field]
            if widgets or not kids:
                found.append(name)
                listed.extend(each.objgen for each in widgets)

        assert sorted(found) == sorted(names)
        assert len(set(listed)) == len(listed)
        assert sorted(listed) == sorted(on_pages)


def assert_round_trip(pdf, data):
    # the wrapper and its reopened output both read these values
    reopened = PdfWrapper(pdf.read(), use_full_widget_name=pdf.use_full_widget_name)
    for name, value in data.items():
        for actual in (pdf.data[name], reopened.data[name]):
            # True == 1 and False == 0, but a checkbox value isn't an index
            assert isinstance(actual, bool) == isinstance(value, bool)
            assert actual == value


def _same_property(actual, expected):
    # numbers are compared approximately, since the PDF stores them as reals,
    # and a list or tuple of choices or per-option geometry element by element
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        return len(actual) == len(expected) and all(
            _same_property(a, b) for a, b in zip(actual, expected, strict=True)
        )
    if isinstance(actual, bool) or isinstance(expected, bool):
        return actual is expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return actual == pytest.approx(expected)

    return actual == expected


# the widget properties that opening a PDF reads from it, independently of
# the widget classes' own READ_PROPERTIES
COMPARED_PROPERTIES = (
    "value",
    "page_number",
    "x",
    "y",
    "width",
    "height",
    "readonly",
    "required",
    "hidden",
    "tooltip",
    "font",
    "font_size",
    "font_color",
    "comb",
    "alignment",
    "multiline",
    "max_length",
    "choices",
    "number_of_options",
)


def assert_widgets_match_output(pdf):
    # the wrapper's fields, values, and properties read from the PDF are the
    # same as those of its reopened output
    stream = pdf.read()
    reopened = PdfWrapper(stream, use_full_widget_name=pdf.use_full_widget_name)
    assert list(pdf.widgets) == list(reopened.widgets)
    for name, widget in pdf.widgets.items():
        other = reopened.widgets[name]
        assert type(widget) is type(other)
        for prop in COMPARED_PROPERTIES:
            actual, expected = (
                getattr(widget, prop, None),
                getattr(other, prop, None),
            )
            if prop == "value" and type(widget) is Checkbox:
                # an unchecked checkbox reads None, filled with False or not
                actual, expected = actual or None, expected or None
            assert _same_property(actual, expected), (name, prop, actual, expected)


def assert_valid_appearances(stream):
    # every appearance is a dictionary of appearance streams, and a widget with
    # appearance states selects one of them or none
    with pikepdf.Pdf.open(BytesIO(stream)) as pdf:
        for page in pdf.pages:
            for annot in page.get("/Annots", []):
                if "/AP" not in annot:
                    continue
                assert isinstance(annot.AP, pikepdf.Dictionary)
                assert "/N" in annot.AP
                for key in ("/N", "/R", "/D"):
                    appearance = annot.AP.get(key)
                    if appearance is None or isinstance(appearance, pikepdf.Stream):
                        continue
                    assert isinstance(appearance, pikepdf.Dictionary)
                    assert all(
                        isinstance(each, pikepdf.Stream) for each in appearance.values()
                    )
                if not isinstance(annot.AP.N, pikepdf.Stream):
                    state = annot.get("/AS")
                    # a string with the same characters selects no state
                    assert isinstance(state, pikepdf.Name)
                    assert str(state) in ("/Off", *annot.AP.N.keys())


def describe_annotations(stream, changed):
    # each page's annotations, without the widgets of the changed fields,
    # described so that they don't depend on object numbers or compression
    with pikepdf.Pdf.open(BytesIO(stream)) as pdf:
        pages = {page.obj.objgen: index for index, page in enumerate(pdf.pages)}

        def get_name(field):
            names = []
            while field is not None:
                if "/T" in field:
                    names.append(str(field.T))
                field = field.get("/Parent")

            return ".".join(reversed(names))

        def describe(obj, seen):
            if not isinstance(obj, pikepdf.Object):
                return repr(obj)
            if obj.is_indirect:
                if obj.objgen in pages:
                    return f"page {pages[obj.objgen] + 1}"
                if obj.objgen in seen:
                    # a reference back to an object that is being described
                    return "seen"
                seen = {*seen, obj.objgen}
            if isinstance(obj, pikepdf.Stream):
                return (
                    {
                        key: describe(value, seen)
                        for key, value in obj.stream_dict.items()
                        if key != "/Length"
                    },
                    _read_stream(obj),
                )
            if isinstance(obj, pikepdf.Dictionary):
                # a field's other widgets are described where their pages list them
                return {
                    key: describe(value, seen)
                    for key, value in obj.items()
                    if key != "/Kids"
                }
            if isinstance(obj, pikepdf.Array):
                return [describe(each, seen) for each in obj]

            return obj.unparse()

        return [
            [
                describe(annot, set())
                for annot in page.get("/Annots", [])
                if annot.get("/Subtype") != pikepdf.Name.Widget
                or get_name(annot) not in changed
            ]
            for page in pdf.pages
        ]


def assert_annotations_preserved(before, after, changed=()):
    # every annotation, other than the widgets of the fields with these fully
    # qualified names, has the same content on the same page in the same order
    assert describe_annotations(after, changed) == describe_annotations(before, changed)
