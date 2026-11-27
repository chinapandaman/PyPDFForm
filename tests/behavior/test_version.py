# -*- coding: utf-8 -*-

import os
from io import BytesIO, StringIO

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NullObject,
    NumberObject,
    TextStringObject,
)

from PyPDFForm import Annotations, Fields, PdfArray, PdfWrapper, RawElements
from PyPDFForm.lib import hooks
from PyPDFForm.lib.constants import FEATURE_HOOKS
from PyPDFForm.lib.middleware.text import Text
from PyPDFForm.lib.utils import (
    get_catalog_version,
    get_output_version,
    get_required_version,
    get_version,
    set_version,
)
from tests.support.builders import (
    blank_pdf,
    pdf_with_catalog_version,
    with_parent_cycle,
    without_default_appearance,
)


def test_version(pdf_samples):
    versions = ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "2.0"]

    for version in versions:
        obj = PdfWrapper(os.path.join(pdf_samples, "versions", f"{version}.pdf"))
        assert obj.version == version
        assert obj.change_version("2.0").version == "2.0"

    obj = PdfWrapper(os.path.join(pdf_samples, "versions", "unknown.pdf"))
    assert obj.version is None
    stream = obj.read()
    assert stream.startswith(b"%PDF-2.1")
    assert get_version(b"not a pdf") is None
    assert set_version(stream, obj.version, None) == stream
    assert set_version(b"not a pdf", None, "2.0") == b"not a pdf"
    assert set_version(b"prefix %PDF-1.7\n", "1.7", "2.0") == b"prefix %PDF-2.0\n"
    assert obj.change_version("2.0").version == "2.0"
    assert obj.read().startswith(b"%PDF-2.0")


@pytest.mark.parametrize("read_version_first", [False, True])
@pytest.mark.parametrize(
    "operation",
    [
        lambda obj: obj.remove_fields(["test"]),
        lambda obj: obj.fill({"test": "test_1"}),
        lambda obj: setattr(obj.widgets["test"], "font_size", 20),
        lambda obj: setattr(obj, "title", "My PDF"),
    ],
    ids=["remove_fields", "fill", "widget_property", "title"],
)
def test_version_kept_after_rewrite(template_stream, operation, read_version_first):
    obj = PdfWrapper(template_stream)
    if read_version_first:
        assert obj.version == "1.7"

    operation(obj)

    assert obj.version == "1.7"
    assert obj.read().startswith(b"%PDF-1.7")
    assert obj.pages[0].version == "1.7"
    assert obj.pages[0].read().startswith(b"%PDF-1.7")


def test_change_version_after_rewrite(template_stream):
    obj = PdfWrapper(template_stream, title="My PDF")
    assert obj.version == "1.7"
    assert obj.read().startswith(b"%PDF-1.7")

    obj.remove_fields(["test"]).change_version("2.0")
    assert obj.version == "2.0"
    assert obj.read().startswith(b"%PDF-2.0")
    assert obj.pages[0].read().startswith(b"%PDF-2.0")

    # the version PDF writers emit by default
    obj.fill({"test_2": "test_2"}).change_version("1.3")
    assert obj.version == "1.3"
    assert obj.read().startswith(b"%PDF-1.3")
    assert obj.pages[0].read().startswith(b"%PDF-1.3")


@pytest.mark.parametrize(
    ("entries", "expected"),
    [
        ({}, None),
        ({"/FontFile2": NullObject()}, "1.1"),
        ({"/OpenAction": ArrayObject()}, "1.1"),
        ({"/S": NameObject("/URI")}, "1.1"),
        ({"/AcroForm": DictionaryObject()}, "1.2"),
        ({"/Subtype": NameObject("/Widget")}, "1.2"),
        ({"/Filter": NameObject("/FlateDecode")}, "1.2"),
        (
            {
                "/Filter": ArrayObject(
                    [NameObject("/ASCIIHexDecode"), NameObject("/FlateDecode")]
                )
            },
            "1.2",
        ),
        ({"/Filter": NameObject("/ASCIIHexDecode")}, None),
        ({"/ToUnicode": NullObject()}, "1.2"),
        ({"/S": NameObject("/JavaScript")}, "1.3"),
        ({"/FT": NameObject("/Sig")}, "1.3"),
        ({"/FT": NameObject("/Tx")}, None),
        ({"/TU": TextStringObject("tooltip")}, "1.3"),
        ({"/Subtype": NameObject("/Stamp")}, "1.3"),
        ({"/Subtype": NameObject("/Highlight")}, "1.3"),
        ({"/Subtype": NameObject("/Underline")}, "1.3"),
        ({"/Subtype": NameObject("/StrikeOut")}, "1.3"),
        ({"/Subtype": NameObject("/Squiggly")}, "1.4"),
        ({"/Subtype": NameObject("/Text")}, None),
        ({"/T": TextStringObject("Reviewer")}, "1.1"),
        ({"/Subtype": DictionaryObject()}, None),
        ({"/SMask": NameObject("/None")}, "1.4"),
        ({"/CA": FloatObject(0.5)}, "1.4"),
        ({"/ca": NumberObject(1)}, "1.4"),
        # a widget's caption in /MK
        ({"/CA": TextStringObject("4")}, None),
        ({"/Ff": NumberObject(1 << 24)}, "1.5"),
        ({"/Ff": NumberObject(1 << 12)}, None),
        ({"/S": NameObject("/JavaScript"), "/Ff": NumberObject(1 << 24)}, "1.5"),
    ],
)
def test_required_version(entries, expected):
    writer = PdfWriter()
    writer.add_blank_page(width=360, height=360)
    add_object = writer._add_object  # type: ignore # noqa: SLF001
    test_dict = DictionaryObject(
        {NameObject(key): value for key, value in entries.items()}
    )
    reference = add_object(test_dict)
    # an indirect value, and a cycle back to the dictionary
    test_dict[NameObject("/Self")] = reference
    writer.root_object[NameObject("/Test")] = add_object(
        ArrayObject([reference, add_object(DictionaryObject())])
    )
    with BytesIO() as f:
        writer.write(f)
        stream = f.getvalue()

    assert get_required_version(stream) == expected


def test_required_version_of_title_and_unreadable_streams():
    writer = PdfWriter()
    writer.add_blank_page(width=360, height=360)
    writer.root_object[NameObject("/Test")] = DictionaryObject(
        {NameObject("/Title"): TextStringObject("not the document title")}
    )
    with BytesIO() as f:
        writer.write(f)
        assert get_required_version(f.getvalue()) is None

    writer.add_metadata({"/Title": "My PDF"})
    with BytesIO() as f:
        writer.write(f)
        assert get_required_version(f.getvalue()) == "1.1"

    assert get_required_version(b"") is None
    assert get_required_version(b"not a pdf") is None


@pytest.mark.parametrize(
    ("version", "baseline", "required", "expected"),
    [
        ("1.7", "1.4", "1.5", "1.7"),
        ("1.1", None, "1.2", "1.2"),
        ("1.1", "1.0", "1.2", "1.2"),
        # the template already understates its own content
        ("1.0", "1.4", "1.2", "1.0"),
        ("1.1", "1.0", None, "1.1"),
        (None, None, "1.2", "1.2"),
        (None, None, None, None),
        ("unknown", None, "1.2", "1.2"),
    ],
)
def test_output_version(version, baseline, required, expected):
    assert get_output_version(version, baseline, required) == expected


@pytest.mark.parametrize(
    ("template_version", "operation", "expected", "expected_page"),
    [
        (
            "1.0",
            lambda obj, font, image: obj.annotate(
                [Annotations.TextAnnotation(1, 10, 10)]
            ),
            "1.0",
            "1.0",
        ),
        (
            "1.0",
            lambda obj, font, image: obj.draw([RawElements.RawText("text", 1, 10, 10)]),
            "1.0",
            "1.0",
        ),
        (
            "1.0",
            lambda obj, font, image: setattr(obj, "title", "My PDF"),
            "1.1",
            "1.1",
        ),
        (
            "1.0",
            lambda obj, font, image: obj.annotate(
                [Annotations.TextAnnotation(1, 10, 10, title="Reviewer")]
            ),
            "1.1",
            "1.1",
        ),
        (
            "1.0",
            lambda obj, font, image: obj.annotate(
                [Annotations.LinkAnnotation(1, 10, 10, uri="https://example.com")]
            ),
            "1.1",
            "1.1",
        ),
        (
            "1.1",
            lambda obj, font, image: obj.bulk_create_fields(
                [Fields.TextField("name", 1, 50, 50, width=100, height=20)]
            ),
            "1.2",
            "1.2",
        ),
        (
            "1.0",
            lambda obj, font, image: obj.register_font("new_font", font),
            "1.2",
            "1.2",
        ),
        (
            "1.2",
            lambda obj, font, image: setattr(
                obj, "on_open_javascript", "app.alert('opened');"
            ),
            "1.3",
            # pages don't copy the document-open action
            "1.2",
        ),
        (
            "1.2",
            lambda obj, font, image: obj.bulk_create_fields(
                [Fields.SignatureField("signature", 1, 50, 50)]
            ),
            "1.3",
            "1.3",
        ),
        (
            "1.2",
            lambda obj, font, image: obj.bulk_create_fields(
                [Fields.TextField("name", 1, 50, 50, tooltip="tooltip")]
            ),
            "1.3",
            "1.3",
        ),
        (
            "1.2",
            lambda obj, font, image: obj.annotate(
                [
                    Annotations.RubberStampAnnotation(1, 10, 10),
                    Annotations.HighlightAnnotation(1, 40, 10),
                    Annotations.UnderlineAnnotation(1, 70, 10),
                    Annotations.StrikeOutAnnotation(1, 100, 10),
                ]
            ),
            "1.3",
            "1.3",
        ),
        (
            "1.3",
            lambda obj, font, image: obj.annotate(
                [Annotations.SquigglyAnnotation(1, 10, 10)]
            ),
            "1.4",
            "1.4",
        ),
        (
            "1.3",
            lambda obj, font, image: obj.draw(
                [RawElements.RawImage(image, 1, 10, 10, 50, 50)]
            ),
            "1.4",
            "1.4",
        ),
        (
            "1.4",
            lambda obj, font, image: obj.bulk_create_fields(
                [Fields.TextField("name", 1, 50, 50, max_length=4, comb=True)]
            ),
            "1.5",
            "1.5",
        ),
        (
            "1.7",
            lambda obj, font, image: obj.bulk_create_fields(
                [Fields.TextField("name", 1, 50, 50, max_length=4, comb=True)]
            ),
            "1.7",
            "1.7",
        ),
    ],
    ids=[
        "text_annotation",
        "draw_text",
        "title",
        "text_annotation_title",
        "uri_link",
        "text_field",
        "register_font",
        "on_open_javascript",
        "signature_field",
        "tooltip",
        "stamp_and_text_markup",
        "squiggly",
        "transparent_image",
        "comb",
        "comb_on_newer_template",
    ],
)
def test_version_raised_for_added_feature(
    sample_font_stream,
    image_samples,
    template_version,
    operation,
    expected,
    expected_page,
):
    obj = PdfWrapper(blank_pdf(template_version))
    operation(
        obj,
        sample_font_stream,
        os.path.join(image_samples, "sample_transparent_png.png"),
    )

    assert obj.version == expected
    assert obj.read().startswith(f"%PDF-{expected}".encode())
    assert obj.pages[0].version == expected_page
    assert obj.pages[0].read().startswith(f"%PDF-{expected_page}".encode())
    assert PdfArray([obj]).merge().read().startswith(f"%PDF-{expected}".encode())


def test_version_kept_when_template_understates_its_content(pdf_samples):
    # the template declares 1.0 but has an AcroForm and constant opacity (1.4)
    obj = PdfWrapper(os.path.join(pdf_samples, "versions", "1.0.pdf"))
    obj.annotate([Annotations.RubberStampAnnotation(1, 10, 10)])
    assert obj.version == "1.0"
    assert obj.read().startswith(b"%PDF-1.0")
    assert obj.pages[0].read().startswith(b"%PDF-1.0")

    obj.bulk_create_fields(
        [Fields.TextField("name", 1, 50, 50, max_length=4, comb=True)]
    )
    assert obj.version == "1.5"
    assert obj.read().startswith(b"%PDF-1.5")


def test_change_version_kept_for_existing_features():
    obj = PdfWrapper(blank_pdf("1.1")).bulk_create_fields(
        [Fields.TextField("name", 1, 50, 50, width=100, height=20)]
    )
    assert obj.version == "1.2"

    obj.change_version("1.1")
    assert obj.version == "1.1"
    assert obj.read().startswith(b"%PDF-1.1")
    assert obj.pages[0].read().startswith(b"%PDF-1.1")
    assert PdfArray([obj]).merge().read().startswith(b"%PDF-1.1")

    obj.annotate([Annotations.RubberStampAnnotation(1, 10, 10)])
    assert obj.version == "1.3"
    assert obj.read().startswith(b"%PDF-1.3")
    assert obj.pages[0].read().startswith(b"%PDF-1.3")


@pytest.mark.parametrize("option", ["need_appearances", "generate_appearance_streams"])
def test_change_version_kept_for_output_options(option):
    # without a change, the AcroForm that read() adds for the option raises 1.1
    assert PdfWrapper(blank_pdf("1.1"), **{option: True}).version == "1.2"

    obj = PdfWrapper(blank_pdf("1.7"), **{option: True}).change_version("1.1")
    assert obj.version == "1.1"
    assert obj.read().startswith(b"%PDF-1.1")
    assert obj.pages[0].read().startswith(b"%PDF-1.1")

    obj.annotate([Annotations.RubberStampAnnotation(1, 10, 10)])
    assert obj.version == "1.3"
    assert obj.read().startswith(b"%PDF-1.3")


@pytest.mark.parametrize("version", ["1.7", "1.4"])
def test_version_keeps_pending_widget_changes(template_stream, version):
    stream = without_default_appearance(template_stream, "test")
    obj = PdfWrapper(set_version(stream, get_version(stream), version))
    assert obj.version == version

    obj.widgets["test"].font_size = 20
    assert obj.version == version
    assert obj.widgets["test"].font_size == 20
    assert obj.widgets["test"].hooks_to_trigger

    # the font size can't be set without a default appearance
    with pytest.raises(ValueError, match="Cannot change /DA"):
        obj.read()


@pytest.mark.parametrize(
    ("template_version", "field_options", "changes", "expected"),
    [
        ("1.2", {}, [("tooltip", "tooltip")], "1.3"),
        ("1.2", {}, [("tooltip", "tooltip"), ("tooltip", "")], "1.2"),
        ("1.2", {}, [("on_hovered_over_javascript", "app.alert('over');")], "1.3"),
        ("1.2", {}, [("on_blurred_javascript", "app.alert('blurred');")], "1.3"),
        # an empty script still writes a JavaScript action
        ("1.2", {}, [("on_focused_javascript", "")], "1.3"),
        ("1.4", {}, [("max_length", 4)], "1.4"),
        ("1.4", {}, [("comb", True)], "1.5"),
        ("1.4", {}, [("comb", False)], "1.4"),
        ("1.4", {}, [("comb", True), ("comb", False)], "1.4"),
        # the only comb field, already written, is cleared
        ("1.4", {"comb": True}, [("comb", False)], "1.4"),
        ("1.4", {"comb": True}, [("comb", False), ("comb", True)], "1.5"),
    ],
)
def test_version_previews_pending_widget_changes(
    template_version, field_options, changes, expected
):
    obj = PdfWrapper(blank_pdf(template_version)).bulk_create_fields(
        [Fields.TextField("name", 1, 50, 50, max_length=4, **field_options)]
    )
    obj.read()
    for name, value in changes:
        setattr(obj.widgets["name"], name, value)
    queued = list(obj.widgets["name"].hooks_to_trigger)

    assert obj.version == expected
    assert obj.widgets["name"].hooks_to_trigger == queued

    assert obj.read().startswith(f"%PDF-{expected}".encode())
    assert obj.version == expected


def test_version_keeps_pending_javascript_file():
    obj = PdfWrapper(blank_pdf("1.2")).bulk_create_fields(
        [Fields.TextField("name", 1, 50, 50)]
    )
    obj.widgets["name"].on_focused_javascript = StringIO("app.alert('focused');")
    assert obj.version == "1.3"

    annotation = PdfReader(BytesIO(obj.read())).pages[0]["/Annots"][0].get_object()
    assert annotation["/AA"]["/Fo"]["/JS"] == "app.alert('focused');"


def test_version_leaves_unreadable_javascript_path_to_read(tmp_path):
    path = tmp_path / "invalid.js"
    path.write_bytes(b"app.alert('\xff\xfe');")
    obj = PdfWrapper(blank_pdf("1.2")).bulk_create_fields(
        [Fields.TextField("name", 1, 50, 50)]
    )
    obj.read()

    obj.widgets["name"].on_focused_javascript = str(path)
    # only whether a script is written matters, so the file isn't opened
    assert obj.version == "1.3"
    assert obj.widgets["name"].hooks_to_trigger

    with pytest.raises(UnicodeDecodeError):
        obj.read()


def test_pending_feature_hooks_are_widget_hooks():
    hook_names = set(
        Text("name").SET_ATTR_TRIGGER_HOOK_MAP.values()
    )  # including those of every widget
    for hook in FEATURE_HOOKS:
        assert hook in hook_names
        assert callable(getattr(hooks, hook))


@pytest.mark.parametrize(
    ("catalog_version", "expected"),
    [
        (NameObject("/1.4"), "1.4"),
        (NameObject("/2.0"), "2.0"),
        (NameObject("/3.0"), None),
        (TextStringObject("1.4"), None),
        (NullObject(), None),
    ],
)
def test_catalog_version(catalog_version, expected):
    stream = pdf_with_catalog_version("1.1", catalog_version)
    assert get_catalog_version(stream) == expected


def test_catalog_version_of_unreadable_streams():
    assert get_catalog_version(b"") is None
    assert get_catalog_version(b"not a pdf") is None
    assert get_catalog_version(blank_pdf("1.1")) is None


def test_pages_keep_catalog_version():
    obj = PdfWrapper(
        pdf_with_catalog_version("1.1", NameObject("/1.4"), squiggly_page=2)
    ).bulk_create_fields([Fields.TextField("name", 1, 50, 50)])

    # the catalog override is kept and covers the new form, so the header is too
    output = obj.read()
    assert output.startswith(b"%PDF-1.1")
    assert PdfReader(BytesIO(output)).root_object["/Version"] == "/1.4"
    assert obj.version == "1.1"

    # the page has no catalog, so the override moves to its header
    assert obj.pages[0].version == "1.4"
    assert obj.pages[0].read().startswith(b"%PDF-1.4")
    assert "/Version" not in PdfReader(BytesIO(obj.pages[0].read())).root_object

    # a feature newer than the override still raises both
    obj.bulk_create_fields(
        [Fields.TextField("comb", 1, 50, 100, max_length=4, comb=True)]
    )
    assert obj.read().startswith(b"%PDF-1.5")
    assert obj.pages[0].read().startswith(b"%PDF-1.5")


def test_catalog_version_keeps_header_of_document_without_new_features():
    obj = PdfWrapper(
        pdf_with_catalog_version("1.1", NameObject("/1.4"))
    ).bulk_create_fields([Fields.TextField("name", 1, 50, 50)])
    assert obj.version == "1.1"
    assert obj.read().startswith(b"%PDF-1.1")
    assert obj.pages[0].read().startswith(b"%PDF-1.4")


def test_version_leaves_failing_comb_change_to_read(template_stream):
    stream = with_parent_cycle(template_stream, "test")
    # below 1.5, the version getter previews queued comb changes
    obj = PdfWrapper(set_version(stream, get_version(stream), "1.4"))
    widget = obj.widgets["test"]
    widget.comb = True

    assert obj.version == "1.4"
    assert widget.hooks_to_trigger

    with pytest.raises(ValueError, match="the /Parent chain of the field has a cycle"):
        obj.read()
    assert widget.comb is False
