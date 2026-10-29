# -*- coding: utf-8 -*-

import os
from collections import Counter
from io import BytesIO

import pytest
from pikepdf import Pdf
from PIL import UnidentifiedImageError
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, TextStringObject

from PyPDFForm import Annotations, PdfWrapper
from PyPDFForm.lib.constants import IMAGE_IMPORT_JAVASCRIPT
from PyPDFForm.lib.patterns import get_widget_key


@pytest.fixture(params=[False, True], ids=["short-names", "full-names"])
def annotated_form(request):
    writer = PdfWriter()
    writer.add_blank_page(612, 792)
    writer.add_blank_page(612, 792)
    fields = []
    for name, field_type, y in (
        ("first", "/Sig", 100),
        ("second", "/Sig", 200),
        ("image", "/Btn", 300),
        ("text", "/Tx", 400),
    ):
        properties = {
            "/Subtype": "/Widget",
            "/FT": field_type,
            "/T": TextStringObject(name),
            "/Rect": [40, y, 200, y + 50],
        }
        if name == "image":
            properties["/A"] = {
                "/S": "/JavaScript",
                "/JS": TextStringObject(IMAGE_IMPORT_JAVASCRIPT),
            }
        if name == "text":
            properties["/V"] = TextStringObject("retained value")
            properties["/DA"] = TextStringObject("/Helv 12 Tf 0 g")
        fields.append(writer.add_annotation(0, properties).indirect_reference)

    roots = ArrayObject(fields)
    if request.param:
        parent = writer._add_object(  # type: ignore # noqa: SLF001
            DictionaryObject(
                {
                    NameObject("/T"): TextStringObject("group"),
                    NameObject("/Kids"): roots,
                }
            )
        )
        for field in fields:
            field.get_object()[NameObject("/Parent")] = parent
        # The same short name under a different parent must remain untouched.
        other = writer.add_annotation(
            1,
            {
                "/Subtype": "/Widget",
                "/FT": "/Sig",
                "/T": TextStringObject("first"),
                "/Rect": [40, 100, 200, 150],
            },
        )
        other_parent = writer._add_object(  # type: ignore # noqa: SLF001
            DictionaryObject(
                {
                    NameObject("/T"): TextStringObject("other"),
                    NameObject("/Kids"): ArrayObject([other.indirect_reference]),
                }
            )
        )
        other[NameObject("/Parent")] = other_parent
        roots = ArrayObject([parent, other_parent])
    writer.root_object[NameObject("/AcroForm")] = DictionaryObject(
        {NameObject("/Fields"): roots}
    )

    note = writer.add_annotation(
        0,
        Annotations.TextAnnotation(
            1,
            300,
            400,
            contents="keep note",
            title="group.first" if request.param else "first",
        ).get_specific_properties(),
    )
    writer.add_annotation(
        0,
        {
            "/Subtype": "/Popup",
            "/Rect": [300, 400, 400, 500],
            "/Parent": note.indirect_reference,
        },
    )
    reply = writer.add_annotation(
        0,
        Annotations.TextAnnotation(
            1, 300, 450, contents="keep reply"
        ).get_specific_properties(),
    )
    reply[NameObject("/IRT")] = note.indirect_reference
    writer.add_annotation(
        0,
        {
            "/Subtype": "/Link",
            "/Rect": [300, 300, 400, 320],
            "/Dest": ArrayObject(
                [writer.pages[1].indirect_reference, NameObject("/Fit")]
            ),
        },
    )
    writer.add_annotation(
        0,
        Annotations.HighlightAnnotation(
            1, 300, 200, width=100, height=20
        ).get_specific_properties(),
    )
    writer.add_annotation(
        1,
        Annotations.TextAnnotation(
            2, 300, 400, contents="second page"
        ).get_specific_properties(),
    )
    if request.param:
        # Annotation arrays and field arrays may themselves be indirect objects.
        for page in writer.pages:
            page[NameObject("/Annots")] = writer._add_object(page.annotations)  # type: ignore # noqa: SLF001
        for reference in roots:
            parent = reference.get_object()
            parent[NameObject("/Kids")] = writer._add_object(parent["/Kids"])  # type: ignore # noqa: SLF001
        writer.root_object["/AcroForm"][NameObject("/Fields")] = writer._add_object(  # type: ignore # noqa: SLF001
            roots
        )
    stream = BytesIO()
    writer.write(stream)
    return PdfWrapper(stream.getvalue(), use_full_widget_name=request.param)


def _collect_field_references(fields):
    leaves = []
    for reference in fields:
        field = reference.get_object()
        if "/Kids" in field:
            assert field["/Kids"]
            leaves.extend(_collect_field_references(field["/Kids"]))
        else:
            leaves.append(reference)
    return leaves


def assert_annotation_graph(stream, expected_keys, use_full_widget_name):
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
    leaves = _collect_field_references(reader.root_object["/AcroForm"]["/Fields"])
    assert set(leaves) == set(widgets.values())
    assert len(leaves) == len(widgets)
    assert expected_keys <= (reader.get_fields() or {}).keys()
    assert (
        set(PdfWrapper(stream, use_full_widget_name=use_full_widget_name).widgets)
        == expected_keys
    )
    with Pdf.open(BytesIO(stream)) as pdf:
        assert pdf.check_pdf_syntax() == []


def test_fill_preserves_unrelated_annotations(annotated_form, image_samples):
    form = annotated_form
    full_names = form.use_full_widget_name
    key = "group.first" if full_names else "first"
    text_key = "group.text" if full_names else "text"
    original_widgets = form.widgets.copy()
    expected_keys = set(original_widgets) - {key}
    image = os.path.join(image_samples, "sample_signature.png")

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
    assert_annotation_graph(stream, expected_keys, full_names)
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
    assert_annotation_graph(form.read(), expected_keys, full_names)

    image_key = "group.image" if full_names else "image"
    form.fill({image_key: image})
    expected_keys.remove(image_key)
    assert set(form.widgets) == expected_keys
    assert_annotation_graph(form.read(), expected_keys, full_names)
    contents = PdfReader(BytesIO(form.read())).pages[0].get_contents()
    assert contents is not None
    assert contents.get_data().count(b" Do") == 2


@pytest.mark.parametrize("annotated_form", [True], indirect=True, ids=["full-names"])
def test_failed_image_fill_preserves_annotations(annotated_form, image_samples):
    form = annotated_form
    original = form.read()
    original_widgets = form.widgets.copy()

    with pytest.raises(UnidentifiedImageError):
        form.fill(
            {
                "group.first": os.path.join(image_samples, "sample_signature.png"),
                "group.image": b"invalid image",
            }
        )

    assert form.widgets == original_widgets
    assert form.read() == original
    assert_annotation_graph(
        form.read(), set(original_widgets), form.use_full_widget_name
    )


def test_fill_removes_empty_signature_field_tree(image_samples):
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
    assert reader.root_object["/AcroForm"]["/Fields"] == []
    assert not reader.get_fields()
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


@pytest.mark.requires_zlib_over_zlib_ng
def test_fill_signature_overlap(pdf_samples, image_samples, request):
    expected_path = os.path.join(
        pdf_samples, "signature", "test_fill_signature_overlap.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(
                pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
            )
        ).fill({"signature": os.path.join(image_samples, "sample_signature.png")})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.requires_zlib_over_zlib_ng
def test_fill_small_icon(pdf_samples, image_samples, request):
    expected_path = os.path.join(pdf_samples, "signature", "test_fill_small_icon.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(
                pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
            )
        )
        obj.fill({"signature": os.path.join(image_samples, "small_icon.png")})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.requires_zlib_over_zlib_ng
def test_fill_small_icon_not_preserve_aspect_ratio(pdf_samples, image_samples, request):
    expected_path = os.path.join(
        pdf_samples, "signature", "test_fill_small_icon_not_preserve_aspect_ratio.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(
                pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
            )
        )
        obj.widgets["signature"].preserve_aspect_ratio = False
        obj.fill({"signature": os.path.join(image_samples, "small_icon.png")})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_vertical_image(pdf_samples, image_samples, request):
    expected_path = os.path.join(
        pdf_samples, "signature", "test_fill_vertical_image.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(
                pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
            )
        )
        obj.fill({"signature": os.path.join(image_samples, "vertical_image.jpg")})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_vertical_image_not_preserve_aspect_ratio(
    pdf_samples, image_samples, request
):
    expected_path = os.path.join(
        pdf_samples,
        "signature",
        "test_fill_vertical_image_not_preserve_aspect_ratio.pdf",
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(
                pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
            )
        )
        obj.widgets["signature"].preserve_aspect_ratio = False
        obj.fill({"signature": os.path.join(image_samples, "vertical_image.jpg")})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
