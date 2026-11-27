# -*- coding: utf-8 -*-
"""
Prepare PDF output and publish serialized PDFs to filesystem paths.

Preparation helpers manage appearance streams and the /NeedAppearances flag,
add the fields of page widget annotations to the AcroForm `/Fields` array, and
remove widget appearances that aren't appearance dictionaries before
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
from typing import Optional
from warnings import catch_warnings, filterwarnings

from pikepdf import Pdf
from pypdf import PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, StreamObject

from .constants import (
    AP,
    COMB,
    DR,
    MULTILINE,
    XFA,
    AcroForm,
    Annots,
    Encoding,
    Fields,
    Font,
    MacRomanEncoding,
    N,
    Parent,
    Q,
    Resources,
    Subtype,
    V,
    Widget,
    WinAnsiEncoding,
)
from .field_tree import share_inline_objects
from .middleware.dropdown import Dropdown
from .middleware.text import Text
from .patterns import (
    check_field_flag,
    get_selected_option,
    get_text_field_style,
    get_widget_type,
    parse_alignment,
    resolve_inherited_entry,
)
from .utils import get_array, get_dictionary, get_entry

# the Python codecs of the font encodings qpdf draws generated appearances in;
# it draws in ASCII with a font of any other encoding
GENERATOR_ENCODINGS = {WinAnsiEncoding: "cp1252", MacRomanEncoding: "mac_roman"}


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
       `generate_appearance_streams` is True, then removing the ones that
       `_remove_unsupported_appearances` describes, so PDF viewers draw those
       fields instead.

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

        result = _remove_unsupported_appearances(result)

    return result


def _remove_unsupported_appearances(pdf: bytes) -> bytes:
    """
    Removes generated appearances that don't show what a field shows.

    qpdf, which generates appearance streams for pikepdf, draws a text field
    or dropdown on a single line, aligned left, with its value (`/V`) encoded
    as its font's `/Encoding` names, `/WinAnsiEncoding` or
    `/MacRomanEncoding`, or else as ASCII, writing `?` for a character the
    encoding doesn't have. So a text field or dropdown loses its appearance
    when it is centered or right aligned, including by the AcroForm's
    default, when it is a multiline or comb text field, when its value has
    such a character, or when it is a dropdown whose selected option, as
    `get_selected_option` reads it, has another displayed text than its
    value. PDF viewers then draw
    it from its value, as after a fill without generated appearances.

    Args:
        pdf (bytes): The PDF with generated appearance streams.

    Returns:
        bytes: The PDF without those appearances, or `pdf` when no widget
            loses one.
    """
    writer = PdfWriter(BytesIO(pdf))
    acroform = get_dictionary(writer.root_object, AcroForm)
    removed = False
    for page in writer.pages:
        for annot in get_array(page, Annots):
            widget = annot.get_object()
            if (
                isinstance(widget, DictionaryObject)
                and AP in widget
                and not _can_generator_draw(widget, acroform)
            ):
                del widget[AP]
                removed = True

    if not removed:
        return pdf

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


def _can_generator_draw(
    widget: DictionaryObject, acroform: Optional[DictionaryObject]
) -> bool:
    """
    Checks whether qpdf's appearance of a widget shows what the field shows.

    Args:
        widget (DictionaryObject): The widget annotation, with the appearance
            qpdf generated.
        acroform (Optional[DictionaryObject]): The AcroForm dictionary, or None.

    Returns:
        bool: False for a text field or dropdown that
            `_remove_unsupported_appearances` removes the appearance of, and
            True for any other widget.
    """
    _type = get_widget_type(widget)
    if _type not in (Text, Dropdown):
        return True

    multiline_or_comb = _type is Text and (
        check_field_flag(widget, MULTILINE) or check_field_flag(widget, COMB)
    )
    aligned = parse_alignment(_resolve_entry(widget, Q, acroform)) in (1, 2)
    return not (multiline_or_comb or aligned) and _can_generator_draw_value(
        widget, _type, acroform
    )


def _can_generator_draw_value(
    widget: DictionaryObject, _type: type, acroform: Optional[DictionaryObject]
) -> bool:
    """
    Checks whether qpdf draws the value of a text field or dropdown as shown.

    Args:
        widget (DictionaryObject): The widget annotation, with the appearance
            qpdf generated.
        _type (type): The widget's middleware type, `Text` or `Dropdown`.
        acroform (Optional[DictionaryObject]): The AcroForm dictionary, or None.

    Returns:
        bool: False for a value with a character the font's encoding doesn't
            have, or a dropdown whose selected option has another displayed
            text than its value, and True otherwise.
    """
    value = _resolve_entry(widget, V, None)
    if not isinstance(value, str):
        return True
    option = get_selected_option(widget) if _type is Dropdown else None
    if option is not None and option.display != value:
        return False
    try:
        value.encode(_get_generator_encoding(widget, acroform))
    except UnicodeEncodeError:
        return False

    return True


def _get_generator_encoding(
    widget: DictionaryObject, acroform: Optional[DictionaryObject]
) -> str:
    """
    Gets the Python codec of the encoding qpdf drew a widget's value in.

    The font is the one the default appearance (`/DA`) names, looked up in
    the generated appearance's resources and then in the AcroForm's default
    resources (`/DR`), as qpdf looks it up.

    Args:
        widget (DictionaryObject): The widget annotation, with the appearance
            qpdf generated.
        acroform (Optional[DictionaryObject]): The AcroForm dictionary, or None.

    Returns:
        str: `cp1252` for `/WinAnsiEncoding`, `mac_roman` for
            `/MacRomanEncoding`, and `ascii` otherwise.
    """
    font_name = get_text_field_style(widget, acroform).font
    appearance = get_dictionary(widget, AP)
    stream = get_dictionary(appearance, N) if appearance is not None else None
    for owner, key in ((stream, Resources), (acroform, DR)):
        resources = get_dictionary(owner, key) if owner is not None else None
        fonts = get_dictionary(resources, Font) if resources is not None else None
        for name, font in (fonts or {}).items():
            # pypdf decodes escapes in names, which the /DA keeps
            if NameObject(name).renumber().decode() == font_name:
                font = font.get_object()
                encoding = (
                    get_entry(font, Encoding)
                    if isinstance(font, DictionaryObject)
                    else None
                )
                return GENERATOR_ENCODINGS.get(str(encoding), "ascii")

    return "ascii"


def _resolve_entry(
    widget: DictionaryObject, key: str, acroform: Optional[DictionaryObject]
) -> object:
    """
    Resolves an inheritable entry, reading a `/Parent` cycle as no entry.

    Args:
        widget (DictionaryObject): The widget annotation.
        key (str): The entry to resolve, such as `/Q`.
        acroform (Optional[DictionaryObject]): The AcroForm dictionary, or None
            for an entry without a document default.

    Returns:
        object: The resolved value, or None.
    """
    try:
        return resolve_inherited_entry(widget, key, acroform).value
    except ValueError:
        return None


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
    explicit operations such as `remove_widgets_by_keys`. Page widgets and
    parents stored inline are first shared with the field tree by
    `share_inline_objects`, which `PdfWrapper` already applies when it loads a
    PDF. An AcroForm dictionary is created when necessary, and null entries
    are treated as absent. A page widget whose appearance (`/AP`) isn't an
    appearance dictionary, such as the value string that earlier versions of
    PyPDFForm wrote or a stream, loses it, so PDF viewers draw the widget
    instead. When no page has
    a widget annotation, the original PDF stream is returned unchanged to
    avoid an unnecessary rewrite.

    Args:
        pdf (bytes): The PDF stream whose AcroForm fields should be updated.

    Returns:
        bytes: The PDF stream with an updated AcroForm `/Fields` array, or the
            original stream when no page has a widget annotation.
    """
    writer = PdfWriter(BytesIO(pdf))
    share_inline_objects(writer)
    root = writer._root_object  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    fields = ArrayObject([])
    seen_fields = set()
    for page in writer.pages:
        for annot in get_array(page, Annots):
            widget = annot.get_object()
            if (
                not isinstance(widget, DictionaryObject)
                or widget.get(Subtype) != Widget
            ):
                continue
            appearance = widget[AP].get_object() if AP in widget else None
            # pypdf's streams are dictionaries too
            if appearance is not None and (
                not isinstance(appearance, DictionaryObject)
                or isinstance(appearance, StreamObject)
            ):
                # such as the value string that earlier versions wrote
                del widget[AP]
            field_ref = _get_root_field_reference(annot)
            field_key = _field_reference_key(field_ref)
            if field_key not in seen_fields:
                fields.append(field_ref)
                seen_fields.add(field_key)

    if not seen_fields:
        return pdf

    acroform = get_dictionary(root, AcroForm)
    if acroform is None:
        acroform = DictionaryObject({})
        root[NameObject(AcroForm)] = acroform
    for field_ref in get_array(acroform, Fields):
        field_key = _field_reference_key(field_ref)
        if field_key not in seen_fields:
            fields.append(field_ref)
            seen_fields.add(field_key)
    acroform[NameObject(Fields)] = fields

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


def _get_root_field_reference(annot):
    """
    Returns the top-level AcroForm field reference for an annotation.

    Widget annotations can be leaf nodes under a parent field dictionary. The
    catalog `/AcroForm/Fields` array must point at root fields rather than
    child widgets, otherwise readers such as pypdf will not expose hierarchical
    fields like radio groups via `get_fields`. The annotation and its parents
    are expected to be referenced indirectly, as `share_inline_objects` makes
    them.

    Args:
        annot: The widget annotation reference.

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
        field_object = parent

    return field


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
