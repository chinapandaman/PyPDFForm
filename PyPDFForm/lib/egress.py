# -*- coding: utf-8 -*-
"""
A module for egress functions.

This module provides functionalities that prepare the final PDF for output (egress),
ensuring that it is properly formatted and ready for the end-user. This includes
managing appearance streams (so form fields display correctly after being filled),
handling the /NeedAppearances flag, and preserving or updating document-level
properties like metadata, title, and OpenAction scripts. It can also rebuild the
AcroForm `/Fields` array from the widget annotations present on each page. These
functions are typically called right before the final PDF byte stream is returned by
the wrapper module.
"""

from functools import lru_cache
from io import BytesIO
from warnings import catch_warnings, filterwarnings

from pikepdf import Pdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, TextStringObject

from .constants import (
    JS,
    XFA,
    AcroForm,
    Annots,
    Fields,
    JavaScript,
    OpenAction,
    Parent,
    Root,
    S,
    Title,
)
from .template import get_widget_key


@lru_cache(maxsize=128)
def appearance_streams_handler(pdf: bytes, generate_appearance_streams: bool) -> bytes:
    """
    Handles appearance streams and the /NeedAppearances flag for a PDF form.

    This function prepares a PDF for output by:
    1. Removing the XFA dictionary if present, as it can interfere with standard
       AcroForm processing.
    2. Setting the /NeedAppearances flag in the AcroForm dictionary, which asks
       PDF viewers to generate appearance streams for form fields.
    3. Optionally generating appearance streams explicitly using pikepdf if
       `generate_appearance_streams` is True.

    The result is cached using lru_cache for performance.

    Args:
        pdf (bytes): The PDF file content as a bytes stream.
        generate_appearance_streams (bool): Whether to explicitly generate appearance streams for all form fields.

    Returns:
        bytes: The modified PDF content as a bytes stream.
    """
    reader = PdfReader(BytesIO(pdf))
    writer = PdfWriter()

    if AcroForm in reader.trailer[Root] and XFA in reader.trailer[Root][AcroForm]:
        del reader.trailer[Root][AcroForm][XFA]

    writer.append(reader)
    writer.set_need_appearances_writer()

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        result = f.read()

    if generate_appearance_streams:
        with Pdf.open(BytesIO(result)) as f, catch_warnings():
            filterwarnings(
                "ignore", message=".*/AcroForm.*"
            )  # handled by rebuild_acroform_fields

            f.generate_appearance_streams()
            with BytesIO() as r:
                f.save(r, deterministic_id=True)
                r.seek(0)
                result = r.read()

    return result


def preserve_pdf_properties(
    pdf: bytes, title: str, script: str, metadata: dict
) -> bytes:
    """
    Preserves and updates PDF properties such as metadata, title, and OpenAction scripts.

    This function allows setting or updating the PDF's title and metadata, and
    attaching a JavaScript script that executes when the PDF is opened. Metadata
    is merged into the reader's current metadata when provided; the title and
    OpenAction JavaScript are written only when non-empty values are supplied.

    Args:
        pdf (bytes): The PDF file content as a bytes stream.
        title (str): The title to be set in the PDF metadata.
        script (str): JavaScript code to be executed when the PDF is opened.
        metadata (dict): The original metadata to preserve.

    Returns:
        bytes: The modified PDF content as a bytes stream.
    """
    reader = PdfReader(BytesIO(pdf))
    writer = PdfWriter()
    writer.append(reader)

    if title or metadata:
        _metadata = reader.metadata or {}
        if metadata:
            _metadata.update(metadata)
        if title:
            _metadata[NameObject(Title)] = TextStringObject(title)

        writer.add_metadata(_metadata)

    if script:
        open_action = DictionaryObject()
        open_action[NameObject(S)] = NameObject(JavaScript)
        open_action[NameObject(JS)] = TextStringObject(script)

        writer._root_object.update({NameObject(OpenAction): open_action})  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


def rebuild_acroform_fields(
    pdf: bytes, widget_keys: set, use_full_widget_name: bool, force: bool = False
) -> bytes:
    """
    Rebuilds the AcroForm `/Fields` array from matching page annotations.

    The existing `/Fields` array is replaced, creating an AcroForm dictionary
    when necessary. Each page annotation is resolved to a widget key, and only
    annotations whose keys are present in `widget_keys` contribute their
    top-level field object to the new array. Page annotation arrays are left
    unchanged. When no matching page annotations are found, the original PDF
    stream is returned unchanged to avoid an unnecessary rewrite unless
    `force` is enabled.

    Args:
        pdf (bytes): The PDF stream whose AcroForm fields should be rebuilt.
        widget_keys (set): Widget keys to include in the rebuilt `/Fields` array.
        use_full_widget_name (bool): Whether to resolve annotations using their
            full widget names, including parent names.
        force (bool): Whether to rewrite `/Fields` even when no matching
            widgets are found. This is useful after removals, where the correct
            rebuilt array may be empty.

    Returns:
        bytes: The PDF stream with a rebuilt AcroForm `/Fields` array, or the
            original stream when there are no matching widgets to rebuild and
            `force` is disabled.
    """
    if not widget_keys and not force:
        return pdf

    writer = PdfWriter(BytesIO(pdf))
    root = writer._root_object  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    fields = ArrayObject([])
    seen_fields = set()
    for page in writer.pages:
        for annot in page.get(Annots, []):
            key = get_widget_key(annot.get_object(), use_full_widget_name)
            if key in widget_keys:
                field_ref = _get_root_field_reference(writer, annot)
                field_key = _field_reference_key(field_ref)
                if field_key not in seen_fields:
                    fields.append(field_ref)
                    seen_fields.add(field_key)

    if not seen_fields and not force:
        return pdf

    if AcroForm not in root:
        root[NameObject(AcroForm)] = DictionaryObject({})
    root[AcroForm][NameObject(Fields)] = fields

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


def _get_root_field_reference(writer: PdfWriter, annot):
    """
    Returns the top-level AcroForm field reference for an annotation.

    Widget annotations can be leaf nodes under a parent field dictionary. The
    catalog `/AcroForm/Fields` array must point at root fields rather than
    child widgets, otherwise readers such as pypdf will not expose hierarchical
    fields like radio groups via `get_fields`.

    Args:
        writer (PdfWriter): The PDF writer that owns the annotation objects.
        annot: The widget annotation reference or object.

    Returns:
        IndirectObject: The top-level AcroForm field reference.
    """
    field = annot
    field_object = field.get_object()
    visited = set()

    while Parent in field_object and id(field_object) not in visited:
        visited.add(id(field_object))
        field = field_object[Parent]
        field_object = field.get_object()

    return _ensure_indirect_reference(writer, field)


def _ensure_indirect_reference(writer: PdfWriter, field):
    """
    Returns an indirect reference for a field object.

    pypdf expects entries in `/AcroForm/Fields` to have an indirect reference
    when it builds field objects. Parent fields cloned from page annotations can
    appear as direct dictionaries that still know their original indirect
    reference, so prefer that before adding a new indirect object.

    Args:
        writer (PdfWriter): The PDF writer that will own newly added objects.
        field: The field reference or direct field object to normalize.

    Returns:
        IndirectObject: An indirect reference to the field object.
    """
    field_object = field.get_object()
    indirect_reference = getattr(field_object, "indirect_reference", None)
    if indirect_reference is not None:
        return indirect_reference

    if hasattr(field, "idnum"):
        return field

    return writer._add_object(field_object)  # type: ignore[attr-defined] # noqa: SLF001 # pylint: disable=W0212


def _field_reference_key(field_ref) -> tuple:
    """
    Returns a stable key for deduplicating root fields in one writer.

    Args:
        field_ref: The field reference to identify.

    Returns:
        tuple: A stable key for the field reference.
    """
    field_object = field_ref.get_object()
    indirect_reference = getattr(field_object, "indirect_reference", field_ref)
    idnum = getattr(indirect_reference, "idnum", None)
    generation = getattr(indirect_reference, "generation", None)
    if idnum is not None:
        return idnum, generation

    return (id(field_object),)
