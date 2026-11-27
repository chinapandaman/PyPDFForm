# -*- coding: utf-8 -*-

import os
from collections import Counter
from io import BytesIO

import pikepdf
import pytest
from pikepdf import Array, Dictionary, Name, Pdf, Stream
from pypdf import PdfReader

from PyPDFForm import PdfWrapper
from PyPDFForm.lib.constants import DR, AcroForm, Font
from PyPDFForm.lib.middleware.checkbox import Checkbox
from PyPDFForm.lib.patterns import get_widget_key
from tests.support.builders import with_actions


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


def without_duplicate_keys(pairs):
    # a JSON object hook that fails on a key written twice
    keys = [key for key, _ in pairs]
    assert len(keys) == len(set(keys)), keys
    return dict(pairs)


def get_link_targets(stream):
    result = []
    with Pdf.open(BytesIO(stream)) as pdf:
        page_numbers = {page.obj.objgen: i + 1 for i, page in enumerate(pdf.pages)}
        for i, page in enumerate(pdf.pages):
            for annot in page.get("/Annots", []):
                if annot.get("/Subtype") != Name.Link:
                    continue
                dest = annot.Dest if "/Dest" in annot else annot.A.get("/D")
                if dest is None:
                    result.append((i + 1, str(annot.A.URI), []))
                else:
                    target = page_numbers.get(getattr(dest[0], "objgen", None))
                    result.append(
                        (i + 1, target, [str(each) for each in list(dest)[1:]])
                    )
    return result


def get_retained_content(stream, markers):
    found = set()
    with Pdf.open(BytesIO(stream)) as pdf:
        for obj in pdf.objects:
            if isinstance(obj, Stream):
                data = obj.read_bytes() + obj.stream_dict.unparse(resolved=True)
            elif isinstance(obj, (Dictionary, Array)):
                data = obj.unparse(resolved=True)
            else:
                continue
            found.update(marker for marker in markers if marker.encode() in data)
    return found


def get_values(field):
    return tuple(str(field[key]) if key in field else None for key in ("/V", "/DV"))


def get_full_name(field):
    parts = []
    while field is not None:
        if "/T" in field:
            parts.append(str(field.T))
        field = field.get("/Parent")
    return ".".join(reversed(parts))


def describe_catalog(stream):
    # the values of the catalog's fields, by the fully qualified names
    # assert_catalog_fields lists, the calculation order, and the other
    # AcroForm entries
    with Pdf.open(BytesIO(stream)) as pdf:
        acroform = pdf.Root.get("/AcroForm", Dictionary())
        values = {}
        pending = list(acroform.get("/Fields", []))
        while pending:
            field = pending.pop()
            kids = list(field.get("/Kids", []))
            pending.extend(kid for kid in kids if "/T" in kid)
            if not kids or any("/T" not in kid for kid in kids):
                values[get_full_name(field)] = str(field.get("/V", ""))

        return {
            "fields": values,
            "calculation_order": [
                get_full_name(field) for field in acroform.get("/CO", [])
            ],
            "entries": sorted(key for key in acroform if key != "/Fields"),
        }


def get_button(pdf):
    return next(
        annot for annot in pdf.pages[0].Annots if annot.get("/T") == "submit_button"
    )


def describe_targets(targets):
    # names as they are, and references as @ followed by their full names
    return [
        f"@{get_full_name(each)}" if isinstance(each, Dictionary) else str(each)
        for each in (targets if isinstance(targets, Array) else [targets])
    ]


def describe_actions(action):
    # the JavaScript or type of the action and the ones after it, in the
    # order they are performed, with "again" for one reached a second time
    result = []
    seen = set()
    pending = [] if action is None else [action]
    while pending:
        each = pending.pop()
        if isinstance(each, Array):
            pending.extend(reversed(list(each)))
            continue
        if each.is_indirect and each.objgen in seen:
            result.append("again")
            continue
        seen.add(each.objgen)
        result.append(str(each.get("/JS", each.get("/N", each.S))))
        if "/Next" in each:
            pending.append(each.Next)
    return result


def describe_removal(template_stream, add, read):
    # the actions read(pdf) finds before removing test, with each action that
    # names only test shown as the Hide it becomes, and after
    stream = with_actions(template_stream, add)
    with Pdf.open(BytesIO(stream)) as pdf:
        before = describe_actions(read(pdf))
    with Pdf.open(BytesIO(PdfWrapper(stream).remove_fields(["test"]).read())) as pdf:
        after = describe_actions(read(pdf))
    return ["/Hide" if each == "/ResetForm" else each for each in before], after


def find_widget(stream, name):
    # the widget annotation of a field, by its short name
    for page in PdfReader(BytesIO(stream)).pages:
        for annot in page.get("/Annots", []):
            annot = annot.get_object()
            if get_widget_key(annot, False) == name:
                return annot

    pytest.fail(f"No widget named {name}.")


def get_normal_appearance(stream, name):
    # the data of the normal appearance stream of a field's widget, by its
    # short name, or None when the widget has no appearance
    appearance = find_widget(stream, name).get("/AP")
    if appearance is None:
        return None

    return appearance.get_object()["/N"].get_object().get_data()


def get_nested_entries(stream, entry="/DA"):
    # the entry of each field of nest_fields, or None without one
    reader = PdfReader(BytesIO(stream))
    inner = find_widget(stream, "test")["/Parent"].get_object()
    return {
        "test": find_widget(stream, "test").get(entry),
        "test_2": find_widget(stream, "test_2").get(entry),
        "inner": inner.get(entry),
        "outer": inner["/Parent"].get_object().get(entry),
        "/AcroForm": reader.root_object["/AcroForm"].get(entry),
    }


def get_widget_states(stream, name):
    # the /AS and /V of each widget with the short name, in page order
    return [
        [annot.get("/AS"), annot.get("/V")]
        for page in PdfReader(BytesIO(stream)).pages
        for annot in (each.get_object() for each in page.get("/Annots", []))
        if annot.get("/Subtype") == "/Widget" and get_widget_key(annot, False) == name
    ]


def get_field_and_widgets(stream, name):
    # a field that has widget kids, and its kids, by the field's name
    reader = PdfReader(BytesIO(stream))
    field = next(
        each.get_object()
        for each in reader.root_object["/AcroForm"]["/Fields"]
        if each.get_object().get("/T") == name
    )
    return field, [kid.get_object() for kid in field["/Kids"]]


def get_checkbox_field_states(stream):
    # the /AS and /V of each widget of the field "check", and the field's /V
    field = find_widget(stream, "check")["/Parent"].get_object()
    return get_widget_states(stream, "check") + [field.get("/V")]


def get_checkbox_and_radio_states(stream):
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


def assert_annotation_graph(
    stream, expected_keys, use_full_widget_name, assert_catalog_fields
):
    reader = PdfReader(BytesIO(stream))
    widgets = {}
    notes = {}
    subtypes = Counter()
    popups = []
    for page in reader.pages:
        for reference in page["/Annots"]:
            annotation = reference.get_object()
            assert annotation["/P"].indirect_reference == page.indirect_reference
            subtypes[annotation["/Subtype"]] += 1
            if annotation["/Subtype"] == "/Widget":
                widgets[get_widget_key(annotation, use_full_widget_name)] = reference
            elif annotation["/Subtype"] == "/Text":
                notes[annotation["/Contents"]] = reference
            elif annotation["/Subtype"] == "/Popup":
                popups.append(reference)
            elif annotation["/Subtype"] == "/Link":
                assert annotation["/Dest"][0] == reader.pages[1].indirect_reference

    assert set(widgets) == expected_keys
    assert subtypes == {
        "/Widget": len(expected_keys),
        "/Text": 3,
        "/Popup": 1,
        "/Link": 1,
        "/Highlight": 1,
    }
    assert set(notes) == {"keep note", "keep reply", "second page"}
    note = notes["keep note"].get_object()
    assert note["/Popup"].indirect_reference == popups[0]
    assert note["/Popup"]["/Parent"].indirect_reference == notes["keep note"]
    assert (
        notes["keep reply"].get_object()["/IRT"].indirect_reference
        == notes["keep note"]
    )
    # The field tree must reference the same surviving widgets as the pages.
    assert_catalog_fields(stream, expected_keys)
    assert (
        set(PdfWrapper(stream, use_full_widget_name=use_full_widget_name).widgets)
        == expected_keys
    )
    with Pdf.open(BytesIO(stream)) as pdf:
        assert pdf.check_pdf_syntax() == []


def page_contents(pdf):
    return [
        contents.get_data()
        for page in PdfReader(BytesIO(pdf.read())).pages
        if (contents := page.get_contents()) is not None
    ]


def font_of_widget(reader, key):
    annotation = next(
        annot.get_object()
        for annot in reader.pages[0]["/Annots"]
        if annot.get_object().get("/T") == key
    )
    return reader.root_object[AcroForm][DR][Font][annotation["/DA"].split()[0]]


def assert_cli_error(result, *expected_messages, output_path=None):
    assert result.exit_code == 2
    for message in expected_messages:
        assert message in result.output
    if output_path is not None:
        assert not os.path.exists(output_path)
