# -*- coding: utf-8 -*-
"""
Prepare PDF output and publish serialized PDFs to filesystem paths.

Preparation helpers manage appearance streams and the /NeedAppearances flag,
and add the fields of page widget annotations to the AcroForm `/Fields` array
before `PdfWrapper.read()` returns the final bytes.

For path output, `write_path()` writes serialized bytes to a sibling temporary
file and closes it before atomic replacement. It follows symlinks, preserves
existing permission bits, and cleans up failed temporary writes.
"""

import os
import stat
from contextlib import suppress
from functools import lru_cache
from io import BytesIO
from tempfile import NamedTemporaryFile
from warnings import catch_warnings, filterwarnings

from pikepdf import Pdf
from pypdf import PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject, NameObject

from .constants import (
    XFA,
    AcroForm,
    Annots,
    Fields,
    Kids,
    Parent,
    Rect,
    Subtype,
    T,
    Widget,
)
from .utils import get_array, get_dictionary


def write_path(dest: str | bytes | os.PathLike, content: bytes) -> None:
    """
    Write serialized content to a sibling temporary file and replace its target.

    Symlinks are followed. Existing permission bits are copied before replacement;
    new files retain the temporary file's private permissions. Other file metadata
    and hard-link relationships are not preserved. Failures before replacement
    leave the destination's bytes unchanged and remove the temporary file.
    """
    path = os.path.realpath(os.fsdecode(dest))
    mode = None
    try:
        destination_stat = os.stat(path)
    except FileNotFoundError:
        pass
    else:
        if not stat.S_ISREG(destination_stat.st_mode):
            message = "The output destination must be a regular file."
            raise OSError(message)
        mode = stat.S_IMODE(destination_stat.st_mode)

    temporary_path = None
    try:
        with NamedTemporaryFile(
            mode="wb", prefix=".pypdfform-", dir=os.path.dirname(path), delete=False
        ) as output:
            temporary_path = output.name
            if output.write(content) != len(content):
                message = "The temporary PDF write was incomplete."
                raise OSError(message)

        if mode is not None:
            os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            with suppress(FileNotFoundError):
                try:
                    os.unlink(temporary_path)
                except PermissionError:
                    # Windows cannot unlink a temporary file made read-only above.
                    os.chmod(temporary_path, stat.S_IRUSR | stat.S_IWUSR)
                    os.unlink(temporary_path)


@lru_cache(maxsize=8)
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
    writer = PdfWriter(BytesIO(pdf))

    root_object = writer._root_object  # type: ignore # noqa: SLF001 # # pylint: disable=W0212
    if AcroForm in root_object and XFA in root_object[AcroForm]:
        del root_object[AcroForm][XFA]

    writer.set_need_appearances_writer()

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        result = f.read()

    if generate_appearance_streams:
        with Pdf.open(BytesIO(result)) as f, catch_warnings():
            filterwarnings(
                "ignore", message=".*/AcroForm.*"
            )  # handled by sync_acroform_fields

            f.generate_appearance_streams()
            with BytesIO() as r:
                f.save(r, deterministic_id=True)
                r.seek(0)
                result = r.read()

    return result


def sync_acroform_fields(pdf: bytes) -> bytes:
    """
    Adds the fields of page widget annotations to the AcroForm `/Fields` array.

    Operations such as creating fields, merging, and splitting pages add cloned
    widget annotations to pages without listing their fields in the catalog.
    This function lists the top-level field of every widget annotation on a
    page, in page order, followed by every other entry the `/Fields` array
    already had, in their original order. Entries are never removed, so fields
    without a widget on a page, such as hidden fields or fields of widget types
    PyPDFForm does not support, are preserved. Removing fields is left to
    explicit operations such as `remove_widgets_by_keys`. A widget annotation
    stored inline in a page's `/Annots` is shared with the field tree through
    `_share_inline_widget`. An AcroForm dictionary is created when necessary,
    and null entries are treated as absent. When no page has a widget
    annotation, the original PDF stream is returned unchanged to avoid an
    unnecessary rewrite.

    Args:
        pdf (bytes): The PDF stream whose AcroForm fields should be updated.

    Returns:
        bytes: The PDF stream with an updated AcroForm `/Fields` array, or the
            original stream when no page has a widget annotation.
    """
    writer = PdfWriter(BytesIO(pdf))
    root = writer._root_object  # type: ignore # noqa: SLF001 # # pylint: disable=W0212
    acroform = get_dictionary(root, AcroForm)
    existing = get_array(acroform, Fields) if acroform is not None else ArrayObject()
    on_pages = {
        id(annot.get_object())
        for page in writer.pages
        for annot in get_array(page, Annots)
    }
    shared = set()

    fields = ArrayObject([])
    seen_fields = set()
    for page in writer.pages:
        annots = get_array(page, Annots)
        for index, annot in enumerate(annots):
            widget = annot.get_object()
            if (
                not isinstance(widget, DictionaryObject)
                or widget.get(Subtype) != Widget
            ):
                continue
            if not isinstance(annot, IndirectObject):
                annot = _share_inline_widget(writer, widget, existing, on_pages, shared)
                annots[index] = annot
            field_ref = _get_root_field_reference(writer, annot)
            field_key = _field_reference_key(field_ref)
            if field_key not in seen_fields:
                fields.append(field_ref)
                seen_fields.add(field_key)

    if not seen_fields:
        return pdf

    if acroform is None:
        acroform = DictionaryObject({})
        root[NameObject(AcroForm)] = acroform
    for field_ref in existing:
        field_key = _field_reference_key(field_ref)
        if field_key not in seen_fields:
            fields.append(field_ref)
            seen_fields.add(field_key)
    acroform[NameObject(Fields)] = fields

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


def _share_inline_widget(
    writer: PdfWriter,
    widget: DictionaryObject,
    root_fields: ArrayObject,
    on_pages: set,
    shared: set,
) -> IndirectObject:
    """
    Returns the indirect reference a page should use for an inline widget.

    Widget annotations should be indirect objects, so that the page and the
    field tree share one object. PDFs saved by earlier versions of PyPDFForm
    can instead list a widget inline in a page's `/Annots`, with a separate
    copy of it in the field tree. When the widget's parent `/Kids`, or the
    AcroForm `/Fields` array for a widget without a parent, has an indirect
    entry that is on no page and has the same `/Subtype`, `/T`, and `/Rect`,
    that entry is updated to the page's widget and reused, so references to
    it, such as `/CO` entries, keep working. Otherwise the widget becomes a
    new indirect object.

    Args:
        writer (PdfWriter): The PDF writer that owns the page and field tree.
        widget (DictionaryObject): The inline widget annotation.
        root_fields (ArrayObject): The AcroForm `/Fields` array.
        on_pages (set): The `id` of every annotation listed by a page.
        shared (set): Object numbers of entries already reused, updated in
            place.

    Returns:
        IndirectObject: The reference that replaces the inline widget.
    """
    parent = get_dictionary(widget, Parent)
    container = get_array(parent, Kids) if parent is not None else root_fields
    for entry in container:
        copy = entry.get_object()
        if (
            isinstance(entry, IndirectObject)
            and entry.idnum not in shared
            and id(copy) not in on_pages
            and _is_copy(copy, widget)
        ):
            shared.add(entry.idnum)
            copy.clear()
            copy.update({key: widget.raw_get(key) for key in widget})
            return entry

    return writer._add_object(widget)  # type: ignore[attr-defined] # noqa: SLF001 # pylint: disable=W0212


def _is_copy(obj: object, widget: DictionaryObject) -> bool:
    """
    Checks whether an object is a copy of a widget annotation.

    Args:
        obj (object): A resolved object, such as a `/Fields` entry.
        widget (DictionaryObject): The widget annotation.

    Returns:
        bool: True if `obj` is a dictionary with the widget's `/Subtype`, `/T`,
            and `/Rect`.
    """
    return (
        isinstance(obj, DictionaryObject)
        and all(obj.get(key) == widget.get(key) for key in (Subtype, T))
        and _get_rect(obj) == _get_rect(widget)
    )


def _get_rect(annot: DictionaryObject) -> list:
    """
    Gets the `/Rect` of an annotation as numbers.

    Args:
        annot (DictionaryObject): The annotation.

    Returns:
        list: The rectangle's coordinates, or an empty list without one.
    """
    return [float(each.get_object()) for each in get_array(annot, Rect)]


def _get_root_field_reference(writer: PdfWriter, annot):
    """
    Returns the top-level AcroForm field reference for an annotation.

    Widget annotations can be leaf nodes under a parent field dictionary. The
    catalog `/AcroForm/Fields` array must point at root fields rather than
    child widgets, otherwise readers such as pypdf will not expose hierarchical
    fields like radio groups via `get_fields`. A parent stored inline in its
    child's `/Parent` is made an indirect object, and the child's `/Parent`
    points at it, so the child and the catalog share one parent.

    Args:
        writer (PdfWriter): The PDF writer that owns the annotation objects.
        annot: The widget annotation reference or object.

    Returns:
        IndirectObject: The top-level AcroForm field reference.
    """
    field = annot
    field_object = field.get_object()
    visited = set()

    while (parent := get_dictionary(field_object, Parent)) is not None and id(
        field_object
    ) not in visited:
        visited.add(id(field_object))
        field = field_object.raw_get(Parent)
        if not isinstance(field, IndirectObject):
            field = _ensure_indirect_reference(writer, parent)
            field_object[NameObject(Parent)] = field
        field_object = parent

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

    result = field
    if not hasattr(field, "idnum"):
        result = writer._add_object(field_object)  # type: ignore[attr-defined] # noqa: SLF001 # pylint: disable=W0212

    return result


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

    result = (id(field_object),)
    if idnum is not None:
        result = idnum, generation

    return result
