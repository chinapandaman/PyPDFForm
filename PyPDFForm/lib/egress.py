# -*- coding: utf-8 -*-
"""
Prepare PDF output and publish serialized PDFs to filesystem paths.

Preparation helpers manage appearance streams and the /NeedAppearances flag,
add the fields of page widget annotations to the AcroForm `/Fields` array, and
make widget appearances valid before `PdfWrapper.read()` returns the final
bytes.

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
from typing import Dict, Optional, cast
from warnings import catch_warnings, filterwarnings

from pikepdf import Pdf
from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    StreamObject,
)

from .constants import (
    AP,
    AS,
    COMB,
    DR,
    MULTILINE,
    XFA,
    AcroForm,
    Annots,
    BBox,
    D,
    Encoding,
    Fields,
    Font,
    Form,
    MacRomanEncoding,
    N,
    Off,
    Parent,
    Q,
    R,
    Resources,
    Subtype,
    Type,
    V,
    WinAnsiEncoding,
    XObject,
)
from .field_tree import is_widget_annotation, share_inline_objects
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.radio import Radio
from .middleware.text import Text
from .patterns import (
    check_field_flag,
    get_field_rect,
    get_selected_option,
    get_text_field_style,
    get_widget_field,
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
    are treated as absent. The appearance (`/AP`) of every page widget is
    made valid, as `_repair_appearance` describes, such as by removing the
    value string that earlier versions of PyPDFForm wrote. When no page has
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
            if not is_widget_annotation(widget):
                continue
            _repair_appearance(writer, widget)
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


def _repair_appearance(writer: PdfWriter, widget: DictionaryObject) -> None:
    """
    Makes the appearance (`/AP`) of a page widget valid.

    An appearance that isn't an appearance dictionary, such as the value
    string that earlier versions of PyPDFForm wrote or a stream, is removed,
    and so is one whose normal appearance (`/N`) is missing or is neither a
    stream nor a dictionary or array of appearance states. When `/N` is a
    dictionary of states, each state must be a stream and the appearance
    state (`/AS`) must name one of them or `/Off`. Otherwise, a checkbox or
    radio button keeps its states, whose names are its export values, as
    `_repair_states` describes, and an `/AS` that names none of them is set to
    the state its value (`/V`) selects, as `_get_state_of_value` describes.
    The same applies when `/N` is an array, whose names PyPDFForm reads as
    states, if a dictionary of them reads and fills like it, as
    `_is_equivalent_array` describes; otherwise, the array is left as it is.
    Any other widget loses its appearance, including a button without an
    `/AS`, which PyPDFForm doesn't read as a checkbox or radio button. The
    rollover (`/R`) and down (`/D`) appearances lose their states that aren't
    streams, as `_get_stream_states` describes. PDF viewers draw a widget
    without an appearance from its value, and use the normal appearance in
    place of a missing rollover or down appearance.

    The repaired entries are new dictionaries in a new appearance dictionary
    of the widget, which shares the old one's appearance streams, so a
    dictionary that other annotations or entries share keeps its entries. The
    values and properties that PyPDFForm reads don't change.

    Args:
        writer (PdfWriter): The writer whose page holds the widget.
        widget (DictionaryObject): The page widget annotation.
    """
    if AP not in widget:
        return
    appearance = widget[AP].get_object()
    normal = get_entry(appearance, N) if _is_appearance_dictionary(appearance) else None
    # pypdf's streams are dictionaries too, so a single appearance passes
    if not isinstance(normal, (DictionaryObject, ArrayObject)):
        del widget[AP]
        return

    changes: Dict[str, Optional[DictionaryObject]] = {}
    if isinstance(normal, ArrayObject) or (
        _is_appearance_dictionary(normal) and not _selects_state(widget, normal)
    ):
        _type = get_widget_type(widget)
        if _type not in (Checkbox, Radio):
            del widget[AP]
            return
        if not isinstance(normal, ArrayObject) or _is_equivalent_array(
            widget, _type, normal
        ):
            _repair_button_states(writer, widget, _type, normal, changes)

    for key in (R, D):
        entry = get_entry(appearance, key)
        if entry is not None and not _is_valid_states_entry(entry):
            changes[key] = _get_stream_states(entry)

    if changes:
        _replace_appearance(widget, cast(DictionaryObject, appearance), changes)


def _repair_button_states(
    writer: PdfWriter,
    widget: DictionaryObject,
    _type: type,
    normal: DictionaryObject | ArrayObject,
    changes: Dict[str, Optional[DictionaryObject]],
) -> None:
    """
    Repairs the normal appearance states and appearance state of a button.

    Args:
        writer (PdfWriter): The writer to add empty streams to.
        widget (DictionaryObject): The checkbox or radio button widget.
        _type (type): Its middleware type, `Checkbox` or `Radio`.
        normal (DictionaryObject | ArrayObject): Its normal appearance
            (`/N`), which doesn't select a valid appearance.
        changes (Dict[str, Optional[DictionaryObject]]): The changed entries
            of its appearance dictionary, which gets a new `/N` when one is
            built.
    """
    if isinstance(normal, ArrayObject) or not _are_streams(normal):
        normal = changes[N] = _repair_states(writer, widget, normal)
    if not _selects_state(widget, normal):
        widget[NameObject(AS)] = _get_state_of_value(widget, _type, normal)


def _is_equivalent_array(
    widget: DictionaryObject, _type: type, states: ArrayObject
) -> bool:
    """
    Checks whether a dictionary of an array's states reads and fills like it.

    `get_radio_value`, `update_checkbox_value`, and `update_radio_value`
    compare and write the array's elements as they are stored, so each must
    be a name, or a string that spells one, such as `(/b)`, and not an
    indirect reference. Filling writes the first state other than `/Off`,
    whose place in a dictionary isn't kept, since qpdf sorts dictionary keys,
    so there must be at most one. `get_checkbox_value` reads an inherited
    value only from a dictionary of states, so a checkbox without a value of
    its own mustn't inherit a name, other than `/Off`, that the array lists.

    Args:
        widget (DictionaryObject): The checkbox or radio button widget.
        _type (type): Its middleware type, `Checkbox` or `Radio`.
        states (ArrayObject): Its normal appearance (`/N`), an array.

    Returns:
        bool: True when a dictionary of the array's states reads and fills
            like the array.
    """
    if not all(isinstance(each, str) and each.startswith("/") for each in states):
        return False
    names = {str(each) for each in states} - {Off}
    if len(names) > 1:
        return False
    if _type is Checkbox and get_entry(widget, V) is None:
        return _get_inherited_name(widget) not in names

    return True


def _get_inherited_name(widget: DictionaryObject) -> Optional[NameObject]:
    """
    Gets the value a checkbox inherits, as `get_checkbox_value` reads it.

    `get_checkbox_value` reads an inherited value only when it is a name, and
    a `/Parent` cycle before a value is found reads as no value.

    Args:
        widget (DictionaryObject): The checkbox widget.

    Returns:
        Optional[NameObject]: The inherited value when it is a name, or None.
    """
    inherited = _resolve_entry(widget, V, None)

    return inherited if isinstance(inherited, NameObject) else None


def _replace_appearance(
    widget: DictionaryObject,
    appearance: DictionaryObject,
    changes: Dict[str, Optional[DictionaryObject]],
) -> None:
    """
    Gives a widget a new appearance dictionary with changed entries.

    The new dictionary has the old one's other entries, sharing their objects,
    so the old one is unchanged for any annotation that shares it.

    Args:
        widget (DictionaryObject): The widget annotation.
        appearance (DictionaryObject): Its appearance dictionary (`/AP`).
        changes (Dict[str, Optional[DictionaryObject]]): The new value of
            each changed entry, or None for an entry to remove.
    """
    appearance = DictionaryObject(appearance.items())
    for key, value in changes.items():
        if value is None:
            del appearance[key]
        else:
            appearance[NameObject(key)] = value
    widget[NameObject(AP)] = appearance


def _is_valid_states_entry(entry: object) -> bool:
    """
    Checks whether a rollover or down appearance is valid.

    Args:
        entry (object): The resolved rollover (`/R`) or down (`/D`)
            appearance.

    Returns:
        bool: True for a stream or a dictionary of streams.
    """
    return isinstance(entry, StreamObject) or (
        _is_appearance_dictionary(entry) and _are_streams(cast(DictionaryObject, entry))
    )


def _is_appearance_dictionary(obj: object) -> bool:
    """
    Checks whether an object is a dictionary and not a stream.

    Args:
        obj (object): The resolved object.

    Returns:
        bool: True for a dictionary, and False for a stream, since pypdf's
            streams are dictionaries too, or any other object.
    """
    return isinstance(obj, DictionaryObject) and not isinstance(obj, StreamObject)


def _are_streams(states: DictionaryObject) -> bool:
    """
    Checks whether every state of an appearance dictionary entry is a stream.

    Args:
        states (DictionaryObject): A dictionary of appearance states, such as
            a normal appearance (`/N`).

    Returns:
        bool: True when every state is a stream, including when there is none.
    """
    return all(isinstance(each.get_object(), StreamObject) for each in states.values())


def _selects_state(widget: DictionaryObject, states: DictionaryObject) -> bool:
    """
    Checks whether a widget's appearance state selects a valid appearance.

    Args:
        widget (DictionaryObject): The widget annotation.
        states (DictionaryObject): Its normal appearance (`/N`), a dictionary
            of appearance states.

    Returns:
        bool: True when every state is a stream and the appearance state
            (`/AS`) is a name for one of them or `/Off`.
    """
    state = get_entry(widget, AS)
    return (
        isinstance(state, NameObject)
        and (state == Off or state in states)
        and _are_streams(states)
    )


def _repair_states(
    writer: PdfWriter,
    widget: DictionaryObject,
    normal: DictionaryObject | ArrayObject,
) -> DictionaryObject:
    """
    Gets the states of a checkbox or radio button's normal appearance as streams.

    A dictionary's states keep their streams, and a state that isn't a stream
    gets an empty one, as `_create_empty_appearance` describes. Each element
    of an array, a name or a string that spells one, such as `(/b)`, as
    `_is_equivalent_array` requires, is a state with an empty stream.

    Args:
        writer (PdfWriter): The writer to add empty streams to.
        widget (DictionaryObject): The checkbox or radio button widget.
        normal (DictionaryObject | ArrayObject): Its normal appearance (`/N`).

    Returns:
        DictionaryObject: A new dictionary of the states, each a stream.
    """
    if isinstance(normal, ArrayObject):
        return DictionaryObject(
            {
                NameObject(state): _create_empty_appearance(writer, widget)
                for state in dict.fromkeys(normal)
            }
        )

    return DictionaryObject(
        {
            NameObject(state): (
                value
                if isinstance(value.get_object(), StreamObject)
                else _create_empty_appearance(writer, widget)
            )
            for state, value in normal.items()
        }
    )


def _get_state_of_value(
    widget: DictionaryObject, _type: type, states: DictionaryObject
) -> NameObject:
    """
    Gets the appearance state that a checkbox or radio button's value selects.

    The value (`/V`) is read and compared with the states as
    `get_checkbox_value` and `get_radio_value` do: a checkbox's own value, or
    else the name it inherits, and the value of the field a radio button
    belongs to, as `get_widget_field` describes. It selects the state other
    than `/Off` whose name has the same text, so a string such as `(/b)`
    selects `/b`. A `/Parent` cycle before a value is found reads as no value.

    Args:
        widget (DictionaryObject): The checkbox or radio button widget.
        _type (type): Its middleware type, `Checkbox` or `Radio`.
        states (DictionaryObject): Its normal appearance (`/N`), a dictionary
            of appearance states.

    Returns:
        NameObject: The state the value selects, or `/Off` when it selects
            none of the widget's states.
    """
    if _type is Radio:
        value = _resolve_entry(get_widget_field(widget), V, None)
    else:
        value = get_entry(widget, V)
        if value is None:
            value = _get_inherited_name(widget)

    return next(
        (NameObject(state) for state in states if state != Off and state == value),
        NameObject(Off),
    )


def _create_empty_appearance(
    writer: PdfWriter, widget: DictionaryObject
) -> IndirectObject:
    """
    Creates an appearance stream that draws nothing.

    Args:
        writer (PdfWriter): The writer to add the stream to.
        widget (DictionaryObject): The widget annotation the stream is for.

    Returns:
        IndirectObject: The new form XObject, whose bounding box (`/BBox`) has
            the width and height of the widget's `/Rect`.
    """
    _, _, width, height = get_field_rect(widget)
    stream = StreamObject()
    stream.update(
        {
            NameObject(Type): NameObject(XObject),
            NameObject(Subtype): NameObject(Form),
            NameObject(BBox): ArrayObject(
                FloatObject(each) for each in (0, 0, width, height)
            ),
        }
    )

    return writer._add_object(stream)  # type: ignore # noqa: SLF001 # # pylint: disable=W0212


def _get_stream_states(entry: object) -> Optional[DictionaryObject]:
    """
    Gets a rollover or down appearance without its states that aren't streams.

    Args:
        entry (object): The resolved rollover (`/R`) or down (`/D`)
            appearance, which is neither a stream nor a dictionary of streams.

    Returns:
        Optional[DictionaryObject]: A new dictionary of its states that are
            streams, or None, which removes the entry, when it isn't a
            dictionary or none of its states is a stream.
    """
    if not _is_appearance_dictionary(entry):
        return None
    states = DictionaryObject(
        (state, value)
        for state, value in cast(DictionaryObject, entry).items()
        if isinstance(value.get_object(), StreamObject)
    )

    return states or None


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
