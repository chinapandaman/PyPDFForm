# -*- coding: utf-8 -*-
"""
Prepare PDF output and publish serialized PDFs to filesystem paths.

Preparation helpers manage appearance streams and the /NeedAppearances flag,
and rebuild the AcroForm `/Fields` array from page widget annotations before
`PdfWrapper.read()` returns the final bytes.

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
from pypdf.generic import ArrayObject, DictionaryObject, NameObject

from .constants import (
    XFA,
    AcroForm,
    Annots,
    Fields,
    Parent,
    Subtype,
    Widget,
)
from .template import get_widget_key


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
            )  # handled by rebuild_acroform_fields

            f.generate_appearance_streams()
            with BytesIO() as r:
                f.save(r, deterministic_id=True)
                r.seek(0)
                result = r.read()

    return result


def rebuild_acroform_fields(
    pdf: bytes, widget_keys: set, use_full_widget_name: bool
) -> bytes:
    """
    Rebuilds the AcroForm `/Fields` array from matching page annotations.

    The existing `/Fields` array is replaced, creating an AcroForm dictionary
    when necessary. Only widget annotations are resolved to a widget key, and
    those whose keys are present in `widget_keys` contribute their
    top-level field object to the new array. Page annotation arrays are left
    unchanged. When no matching page annotations are found, the original PDF
    stream is returned unchanged to avoid an unnecessary rewrite.

    Args:
        pdf (bytes): The PDF stream whose AcroForm fields should be rebuilt.
        widget_keys (set): Widget keys to include in the rebuilt `/Fields` array.
        use_full_widget_name (bool): Whether to resolve annotations using their
            full widget names, including parent names.

    Returns:
        bytes: The PDF stream with a rebuilt AcroForm `/Fields` array, or the
            original stream when there are no matching widgets to rebuild.
    """
    if not widget_keys:
        return pdf

    writer = PdfWriter(BytesIO(pdf))
    root = writer._root_object  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    fields = ArrayObject([])
    seen_fields = set()
    for page in writer.pages:
        for annot in page.get(Annots, []):
            annotation = annot.get_object()
            if (
                annotation.get(Subtype) != Widget
                or get_widget_key(annotation, use_full_widget_name) not in widget_keys
            ):
                continue
            field_ref = _get_root_field_reference(writer, annot)
            field_key = _field_reference_key(field_ref)
            if field_key not in seen_fields:
                fields.append(field_ref)
                seen_fields.add(field_key)

    if not seen_fields:
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
