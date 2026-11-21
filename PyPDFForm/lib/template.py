# -*- coding: utf-8 -*-
"""
Module for handling PDF form templates.

This module provides functionalities to read and update document metadata, set
document-level actions, and extract, build, and update widgets in PDF form
templates. It leverages the pypdf library for PDF manipulation and defines
specific patterns for identifying and constructing different types of widgets.
"""

from copy import deepcopy
from functools import lru_cache
from io import BytesIO
from collections.abc import Callable
from typing import Dict, List, Optional, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    IndirectObject,
    NameObject,
    TextStringObject,
)

from .annotations import AnnotationTypes, LinkAnnotation
from .constants import (
    CO,
    COMB,
    JS,
    MULTILINE,
    READ_ONLY,
    REQUIRED,
    AcroForm,
    Annots,
    Dest,
    Fields,
    JavaScript,
    Kids,
    OpenAction,
    P,
    Parent,
    Rect,
    S,
    Subtype,
    T,
    Title,
    Widget,
)
from .middleware import WIDGET_TYPES
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.radio import Radio
from .middleware.text import Text
from .patterns import (
    WIDGET_DESCRIPTION_PATTERNS,
    WIDGET_TYPE_PATTERNS,
    check_field_flag,
    get_checkbox_value,
    get_dropdown_choices,
    get_dropdown_value,
    get_field_hidden,
    get_field_rect,
    get_radio_value,
    get_text_field_alignment,
    get_text_field_max_length,
    get_text_value,
    get_widget_key,
    update_annotation_name,
)
from .utils import (
    extract_widget_property,
    find_pattern_match,
    get_array,
    get_dictionary,
    get_version,
    set_version,
)


def get_metadata(pdf: bytes) -> dict:
    """
    Retrieves the metadata of a PDF.

    Args:
        pdf (bytes): The PDF stream to extract metadata from.

    Returns:
        dict: A dictionary containing the PDF's metadata.
    """
    result = {}
    if pdf:
        reader = PdfReader(BytesIO(pdf))
        result = reader.metadata or {}

    return result


def get_title(pdf: bytes) -> str | None:
    """
    Retrieves the title from a PDF's document metadata.

    Args:
        pdf (bytes): The PDF stream from which to retrieve the title.

    Returns:
        str | None: The document title, or None when no title is present.
    """
    return get_metadata(pdf).get(Title)


def get_on_open_javascript(pdf: bytes) -> str | None:
    """
    Retrieves the JavaScript configured to run when a PDF is opened.

    Only a document-catalog `/OpenAction` whose action type is JavaScript is
    returned.

    Args:
        pdf (bytes): The PDF stream to inspect for a document-open action.

    Returns:
        str | None: The JavaScript source, or None when the stream is empty or
            does not contain a JavaScript document-open action.
    """
    result = None
    if pdf:
        reader = PdfReader(BytesIO(pdf))
        root_object = reader.root_object
        if OpenAction in root_object and root_object[OpenAction].get(S) == JavaScript:
            result = root_object[OpenAction].get(JS)

    return result


def set_metadata(pdf: bytes, metadata: dict) -> bytes:
    """
    Merges metadata into a PDF's existing document metadata.

    Existing entries are retained unless the supplied mapping contains the
    same key, in which case the supplied value replaces the existing value.

    Args:
        pdf (bytes): The PDF stream whose metadata should be updated.
        metadata (dict): Metadata entries to add or replace.

    Returns:
        bytes: The PDF stream containing the merged metadata.
    """
    writer = PdfWriter(BytesIO(pdf))
    _metadata = writer.metadata or {}
    _metadata.update(metadata)
    writer.add_metadata(_metadata)

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


def set_title(pdf: bytes, title: str) -> bytes:
    """
    Sets a PDF's document title while preserving its other metadata.

    Args:
        pdf (bytes): The PDF stream whose title should be set.
        title (str): The document title to store in the PDF metadata.

    Returns:
        bytes: The PDF stream containing the updated title.
    """
    return set_metadata(pdf, {Title: title})


def set_on_open_javascript(pdf: bytes, script: str) -> bytes:
    """
    Sets a PDF's document-open action to execute JavaScript.

    The script is written to the document catalog as a JavaScript
    `/OpenAction`, replacing any existing document-open action. An action is
    written even when `script` is empty.

    Args:
        pdf (bytes): The PDF stream whose document-open action should be set.
        script (str): JavaScript to execute when the PDF is opened.

    Returns:
        bytes: The PDF stream containing the JavaScript `/OpenAction`.
    """
    writer = PdfWriter(BytesIO(pdf))

    open_action = DictionaryObject()
    open_action[NameObject(S)] = NameObject(JavaScript)
    open_action[NameObject(JS)] = TextStringObject(script)

    writer._root_object.update({NameObject(OpenAction): open_action})  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


def build_widgets(
    pdf_stream: bytes,
    use_full_widget_name: bool,
) -> Dict[str, WIDGET_TYPES]:
    """
    Builds an independent dictionary of widgets from a PDF stream.

    Widget discovery and construction are cached internally, then deep-copied
    before returning so callers can safely mutate widget attributes without
    changing cached objects or widgets returned by other calls.

    Args:
        pdf_stream (bytes): The PDF stream to parse.
        use_full_widget_name (bool): Whether to use the full widget name
            (including parent names) as the widget key.

    Returns:
        Dict[str, WIDGET_TYPES]: A dictionary of widgets, where keys are widget
            keys and values are widget objects.
    """
    return deepcopy(_build_widget_cache(pdf_stream, use_full_widget_name))


@lru_cache(maxsize=8)
def _build_widget_cache(
    pdf_stream: bytes,
    use_full_widget_name: bool,
) -> Dict[str, WIDGET_TYPES]:
    """
    Builds and caches reusable widget objects from a PDF stream.

    The cached widgets must be treated as prototypes only. Use `build_widgets`
    to get independent copies that are safe to mutate.

    Args:
        pdf_stream (bytes): The PDF stream to parse.
        use_full_widget_name (bool): Whether to use the full widget name
            (including parent names) as the widget key.

    Returns:
        Dict[str, WIDGET_TYPES]: Cached widget prototypes keyed by widget name.
    """
    results = {}

    for page_num, widgets in get_widgets_by_page(pdf_stream).items():
        for widget in widgets:
            _process_widget(widget, page_num, use_full_widget_name, results)

    return results


def _process_widget(
    widget: dict,
    page_number: int,
    use_full_widget_name: bool,
    results: Dict[str, WIDGET_TYPES],
) -> None:
    """
    Processes a single widget and adds it to the results dictionary.

    Common geometry and flags are populated for every recognized widget. Text,
    checkbox, dropdown, and radio widgets then get type-specific state. Radio
    annotations that share a key are aggregated into one middleware object with
    per-option geometry and a selected option index.

    Args:
        widget (dict): The widget dictionary from the PDF.
        page_number (int): The 1-indexed page number the widget appears on.
        use_full_widget_name (bool): Whether to use the full widget name.
        results (Dict[str, WIDGET_TYPES]): The dictionary of widgets being built.
    """
    key = get_widget_key(widget, use_full_widget_name)
    _widget = construct_widget(widget, key)
    if _widget is not None:
        _populate_common_properties(widget, page_number, _widget)

        if isinstance(_widget, Text):
            _populate_text_properties(widget, _widget)

        if type(_widget) is Checkbox:
            _widget.value = get_checkbox_value(widget)

        if isinstance(_widget, Dropdown):
            _populate_dropdown_properties(widget, _widget)

        if isinstance(_widget, Radio):
            _handle_radio_widget(widget, key, _widget, results)
        else:
            results[key] = _widget


def _populate_common_properties(
    widget: dict, page_number: int, _widget: WIDGET_TYPES
) -> None:
    """
    Populates common properties for a widget.

    Properties are written directly to ``__dict__`` so extracting existing PDF
    state does not queue update hooks on the middleware object.

    Args:
        widget (dict): The widget dictionary from the PDF.
        page_number (int): The 1-indexed page number the widget appears on.
        _widget (WIDGET_TYPES): The widget object to populate.
    """
    # widget property extractions don't trigger hooks in this function
    _widget.__dict__["page_number"] = page_number
    _widget.__dict__["tooltip"] = extract_widget_property(
        widget, WIDGET_DESCRIPTION_PATTERNS, None, str
    )
    _widget.__dict__["readonly"] = check_field_flag(widget, READ_ONLY)
    _widget.__dict__["required"] = check_field_flag(widget, REQUIRED)
    _widget.__dict__["hidden"] = get_field_hidden(widget)

    (
        _widget.__dict__["x"],
        _widget.__dict__["y"],
        _widget.__dict__["width"],
        _widget.__dict__["height"],
    ) = get_field_rect(widget)


def _populate_text_properties(widget: dict, _widget: Text) -> None:
    """
    Populates properties specific to text widgets.

    This includes text flags, alignment, maximum length, and current value. The
    attributes are assigned directly where needed so loading existing PDF state
    does not trigger write hooks.

    Args:
        widget (dict): The widget dictionary from the PDF.
        _widget (Text): The text widget object to populate.
    """
    _widget.__dict__["comb"] = check_field_flag(widget, COMB)
    _widget.__dict__["alignment"] = get_text_field_alignment(widget)
    _widget.__dict__["multiline"] = check_field_flag(widget, MULTILINE)
    _widget.__dict__["max_length"] = get_text_field_max_length(widget)
    get_text_value(widget, _widget)


def _populate_dropdown_properties(widget: dict, _widget: Dropdown) -> None:
    """
    Populates properties specific to dropdown widgets.

    Dropdown choices are assigned directly before reading the selected value so
    the value can be normalized to an option index without queuing update hooks.

    Args:
        widget (dict): The widget dictionary from the PDF.
        _widget (Dropdown): The dropdown widget object to populate.
    """
    # actually used for filling value
    # doesn't trigger hook
    _widget.__dict__["choices"] = get_dropdown_choices(widget)
    get_dropdown_value(widget, _widget)


def _handle_radio_widget(
    widget: dict, key: str, _widget: Radio, results: Dict[str, WIDGET_TYPES]
) -> None:
    """
    Handles the logic for radio widgets, including aggregating multiple options.

    Each radio annotation contributes one option to a shared `Radio` object. The
    method stores per-option rectangles as lists, increments the option count for
    schema generation, and records the selected option index when the annotation
    is currently selected.

    Args:
        widget (dict): The widget dictionary from the PDF.
        key (str): The widget key.
        _widget (Radio): The radio widget object.
        results (Dict[str, WIDGET_TYPES]): The dictionary of widgets being built.
    """
    field_rect = get_field_rect(widget)

    if key not in results:
        _widget.__dict__["x"] = []
        _widget.__dict__["y"] = []
        _widget.__dict__["width"] = []
        _widget.__dict__["height"] = []
        results[key] = _widget

    radio = cast(Radio, results[key])
    # for schema
    radio.number_of_options += 1

    if isinstance(radio.x, list):
        radio.x.append(field_rect[0])
    if isinstance(radio.y, list):
        radio.y.append(field_rect[1])
    if isinstance(radio.width, list):
        radio.__dict__["width"].append(field_rect[2])
    if isinstance(radio.height, list):
        radio.__dict__["height"].append(field_rect[3])

    if get_radio_value(widget):
        radio.value = radio.number_of_options - 1


def get_widgets_by_page(pdf: bytes) -> Dict[int, List[dict]]:
    """
    Retrieves widgets from a PDF stream, organized by page number.

    This function parses a PDF stream and extracts recognized widget annotations
    present on each page. It returns a dictionary for every page in the document;
    pages without recognized widgets are mapped to empty lists.

    Args:
        pdf (bytes): The PDF stream to parse.

    Returns:
        Dict[int, List[dict]]: A dictionary where keys are page numbers (1-indexed)
            and values are lists of widget dictionaries.
    """
    pdf_file = PdfReader(BytesIO(pdf))

    result = {}

    for i, page in enumerate(pdf_file.pages):
        result[i + 1] = _get_widgets_on_page(page)

    return result


def _get_widgets_on_page(page) -> List[dict]:
    """
    Retrieves widgets from a single PDF page.

    Page annotations are dereferenced and copied into plain dictionaries before
    they are filtered against the supported widget patterns.

    Args:
        page: The PDF page object.

    Returns:
        List[dict]: A list of widget dictionaries found on the page.
    """
    widgets = page.annotations
    result = []
    if widgets:
        for widget in widgets:
            widget = dict(widget.get_object())
            if _is_widget(widget):
                result.append(widget)
    return result


def _is_widget(widget: dict) -> bool:
    """
    Checks if a dictionary represents a valid widget.

    A widget is considered valid when it satisfies all patterns for one of the
    supported middleware widget types.

    Args:
        widget (dict): The dictionary to check.

    Returns:
        bool: True if the dictionary represents a widget, False otherwise.
    """
    for each in WIDGET_TYPE_PATTERNS:
        patterns = each[0]
        check = True
        for pattern in patterns:
            check = check and find_pattern_match(pattern, widget)
        if check:
            return True
    return False


def construct_widget(widget: dict, key: str) -> WIDGET_TYPES | None:
    """
    Constructs a widget object based on the widget dictionary and key.

    This function determines the type of widget based on predefined patterns
    and constructs the corresponding middleware widget object using the supplied
    key as its name.

    Args:
        widget (dict): The widget dictionary to construct the object from.
        key (str): The key of the widget.

    Returns:
        WIDGET_TYPES | None: The constructed widget object, or None
            if the widget type is not recognized.
    """
    result = None
    for each in WIDGET_TYPE_PATTERNS:
        patterns, _type = each
        check = True
        for pattern in patterns:
            check = check and find_pattern_match(pattern, widget)
        if check:
            result = _type(key)
            break
    return result


def _group_annotations_by_page(
    annotations: List[AnnotationTypes],
) -> Dict[int, List[AnnotationTypes]]:
    """
    Groups annotations by their page number.

    Args:
        annotations (List[AnnotationTypes]): A list of annotation objects.

    Returns:
        Dict[int, List[AnnotationTypes]]: A dictionary where keys are page
            numbers and values are lists of annotations for that page.
    """
    result = {}
    for annotation in annotations:
        if annotation.page_number not in result:
            result[annotation.page_number] = []
        result[annotation.page_number].append(annotation)
    return result


def _get_annotation_properties(
    annotation: AnnotationTypes,
    page_references: List[IndirectObject],
) -> dict:
    """
    Builds the PDF dictionary of an annotation for a target PDF.

    A link to an internal page gets a destination that refers to the target
    page in `page_references`.

    Args:
        annotation (AnnotationTypes): The annotation object to build.
        page_references (List[IndirectObject]): References to the pages of the
            target PDF, in page order.

    Returns:
        dict: The PDF dictionary of the annotation.
    """
    result = annotation.get_specific_properties()
    if isinstance(annotation, LinkAnnotation):
        destination = annotation.get_destination(page_references)
        if destination is not None:
            result[NameObject(Dest)] = destination
    return result


def create_annotations(
    template: bytes,
    annotations: List[AnnotationTypes],
) -> bytes:
    """
    Creates and adds annotations to a PDF template.

    This function takes a PDF template and a list of annotation objects, builds
    their PDF dictionaries, and appends them to the `/Annots` array for each
    target page. Existing annotations are preserved, and annotation page numbers
    are 1-based. Links to internal pages refer to the target page objects, and
    every annotation is built before any page changes.

    Args:
        template (bytes): The PDF template to add annotations to.
        annotations (List[AnnotationTypes]): A list of annotation objects to be
            added to the PDF.

    Returns:
        bytes: The updated PDF stream with the added annotations.

    Raises:
        ValueError: If a link points to a page outside the PDF.
    """
    writer = PdfWriter(BytesIO(template))
    page_references = [page.indirect_reference for page in writer.pages]
    annotations_by_page = {
        page_num: [
            _get_annotation_properties(annotation, page_references)
            for annotation in page_annotations
        ]
        for page_num, page_annotations in _group_annotations_by_page(
            annotations
        ).items()
    }

    for i, page in enumerate(writer.pages):
        page_num = i + 1
        if page_num not in annotations_by_page:
            continue

        page_annotations = ArrayObject(annotations_by_page[page_num])
        if Annots in page:
            page[NameObject(Annots)] += page_annotations
        else:
            page[NameObject(Annots)] = page_annotations

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


def remove_widgets_by_keys(
    pdf: bytes, keys: List[str], use_full_widget_name: bool = False
) -> bytes:
    """
    Removes the form fields with the given keys from a PDF.

    A key matches a widget annotation on a page, or a terminal field anywhere
    in the AcroForm field tree, including fields without a widget on any page,
    using the same key rules as `build_widgets`. Matching widgets, and widgets
    of matching fields, are removed from page `/Annots` arrays, and the other
    annotations keep their references. Matching fields and widgets are then
    detached from the field tree with `detach_field`, and every detached field
    is removed from the AcroForm `/CO` calculation order, which is deleted
    when it becomes empty. Detached objects are no longer form fields, but
    other objects that refer to them, such as form actions, are not changed.
    Null entries, such as a null `/CO`, are treated as absent. `get_field_keys`
    lists the keys this function can match. If no keys are provided, the
    original PDF stream is returned unchanged.

    Args:
        pdf (bytes): The PDF stream to remove fields from.
        keys (List[str]): A list of field keys to remove.
        use_full_widget_name (bool): Whether to match fields by their full
            names, including parent names.

    Returns:
        bytes: The updated PDF stream with the matching fields removed.
    """
    if not keys:
        return pdf

    key_set = set(keys)
    writer = PdfWriter(BytesIO(pdf))
    acroform = get_dictionary(writer.root_object, AcroForm) or DictionaryObject()

    matched = {
        id(field): field
        for field in _get_terminal_fields(acroform)
        if get_widget_key(field, use_full_widget_name) in key_set
    }

    for page in writer.pages:
        annots = get_array(page, Annots)
        page_annots = ArrayObject([])
        for reference in annots:
            annot = reference.get_object()
            if _is_widget_annotation(annot) and (
                get_widget_key(annot, use_full_widget_name) in key_set
                or _has_ancestor_in(annot, matched)
            ):
                matched.setdefault(id(annot), annot)
            else:
                page_annots.append(reference)

        if len(page_annots) != len(annots):
            page[NameObject(Annots)] = page_annots

    detached = {}
    for field in matched.values():
        if not _has_ancestor_in(field, matched):
            detached.update((id(each), each) for each in detach_field(writer, field))

    calculation_order = get_array(acroform, CO)
    if calculation_order:
        calculation_order[:] = [
            reference
            for reference in calculation_order
            if not _is_detached(reference.get_object(), detached)
        ]
        if not calculation_order:
            del acroform[CO]

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


def get_field_keys(pdf: bytes, use_full_widget_name: bool) -> set:
    """
    Gets the keys that `remove_widgets_by_keys` can match in a PDF.

    These are the keys of the terminal fields in the AcroForm field tree and of
    the widget annotations on pages, using the same key rules as
    `build_widgets`. Unlike `build_widgets`, fields without a widget on any
    page and widgets of types PyPDFForm does not support are included.

    Args:
        pdf (bytes): The PDF stream to read.
        use_full_widget_name (bool): Whether to use full names, including
            parent names, as keys.

    Returns:
        set: The keys of the terminal fields and page widgets.
    """
    reader = PdfReader(BytesIO(pdf))
    acroform = get_dictionary(reader.root_object, AcroForm) or DictionaryObject()
    page_widgets = [
        annot
        for page in reader.pages
        for annot in (each.get_object() for each in get_array(page, Annots))
        if _is_widget_annotation(annot)
    ]

    return {
        get_widget_key(each, use_full_widget_name)
        for each in _get_terminal_fields(acroform) + page_widgets
    }


def _is_widget_annotation(obj: object) -> bool:
    """
    Checks whether an object is a widget annotation dictionary.

    Args:
        obj (object): A resolved object, such as a page annotation.

    Returns:
        bool: True if `obj` is a dictionary whose `/Subtype` is `/Widget`.
    """
    return isinstance(obj, DictionaryObject) and obj.get(Subtype) == Widget


def _get_terminal_fields(acroform: DictionaryObject) -> List[DictionaryObject]:
    """
    Collects the terminal fields of an AcroForm field tree.

    A terminal field has no `/Kids`, or only kids without a `/T`, which are its
    widget annotations. Other fields are walked into, and each object is
    visited once.

    Args:
        acroform (DictionaryObject): The AcroForm dictionary.

    Returns:
        List[DictionaryObject]: The terminal fields, in tree order.
    """
    result = []
    stack = list(reversed(get_array(acroform, Fields)))
    seen = set()
    while stack:
        field = stack.pop().get_object()
        if isinstance(field, DictionaryObject) and id(field) not in seen:
            seen.add(id(field))
            kids = get_array(field, Kids)
            if any(
                isinstance(kid.get_object(), DictionaryObject) and T in kid.get_object()
                for kid in kids
            ):
                stack.extend(reversed(kids))
            else:
                result.append(field)

    return result


def _has_ancestor_in(
    obj: DictionaryObject, objects: Dict[int, DictionaryObject]
) -> bool:
    """
    Checks whether any object along the `/Parent` chain of an object is listed.

    Args:
        obj (DictionaryObject): A field or widget annotation.
        objects (Dict[int, DictionaryObject]): Objects keyed by their `id`.

    Returns:
        bool: True if an ancestor of `obj` is in `objects`.
    """
    seen = {id(obj)}
    node = get_dictionary(obj, Parent)
    while node is not None and id(node) not in seen:
        if id(node) in objects:
            return True
        seen.add(id(node))
        node = get_dictionary(node, Parent)

    return False


def _is_detached(obj: object, detached: Dict[int, DictionaryObject]) -> bool:
    """
    Checks whether an object or one of its ancestors was detached.

    Args:
        obj (object): A resolved object, such as a `/CO` entry.
        detached (Dict[int, DictionaryObject]): Detached objects keyed by `id`.

    Returns:
        bool: True if `obj` is a detached field or widget, or a descendant of one.
    """
    return id(obj) in detached or (
        isinstance(obj, DictionaryObject) and _has_ancestor_in(obj, detached)
    )


def detach_field(writer: PdfWriter, field: DictionaryObject) -> List[DictionaryObject]:
    """
    Detaches a field or widget and its emptied ancestors from the AcroForm tree.

    The object is removed from its parent's `/Kids`, or from the AcroForm's
    root `/Fields` array when it has no parent. A parent left without kids is
    detached the same way, stopping at the first parent with remaining kids.
    Resolved objects are compared by identity so unrelated fields with the
    same name keep their references. Page annotations are not changed.

    Args:
        writer (PdfWriter): The PDF writer that owns the field tree.
        field (DictionaryObject): The field or widget annotation to detach.

    Returns:
        List[DictionaryObject]: The detached objects: `field` followed by each
            emptied ancestor.
    """
    result = [field]
    parent = get_dictionary(field, Parent)
    while parent is not None:
        kids = get_array(parent, Kids)
        kids[:] = [kid for kid in kids if kid.get_object() is not field]
        if kids or any(parent is each for each in result):
            return result
        field = parent
        result.append(field)
        parent = get_dictionary(field, Parent)

    acroform = get_dictionary(writer.root_object, AcroForm) or DictionaryObject()
    fields = get_array(acroform, Fields)
    fields[:] = [
        reference for reference in fields if reference.get_object() is not field
    ]

    return result


@lru_cache(maxsize=8)
def share_inline_fields(pdf: bytes) -> bytes:
    """
    Shares inline widget annotations and parent fields with the field tree.

    Widget annotations and fields should be indirect objects, so that a page
    and the field tree share one object. PDFs saved by earlier versions of
    PyPDFForm can list a widget inline in a page's `/Annots`, or a field inline
    in its child's `/Parent`, with a separate copy in the field tree. Such PDFs
    are rewritten with `share_inline_objects`, keeping their header version.
    Other PDFs, including empty streams, are returned unchanged. The result is
    cached using lru_cache for performance.

    Args:
        pdf (bytes): The PDF stream to read.

    Returns:
        bytes: The PDF stream whose page widgets and their parents are indirect
            objects shared with the field tree.
    """
    if not pdf or not _has_inline_fields(PdfReader(BytesIO(pdf))):
        return pdf

    writer = PdfWriter(BytesIO(pdf))
    share_inline_objects(writer)
    with BytesIO() as f:
        writer.write(f)
        result = f.getvalue()

    return set_version(result, get_version(result), get_version(pdf))


def _has_inline_fields(reader: PdfReader) -> bool:
    """
    Checks whether a page lists an inline widget or one with an inline parent.

    Args:
        reader (PdfReader): The PDF reader.

    Returns:
        bool: True if a widget annotation in a page's `/Annots`, or a field on
            its `/Parent` chain, is stored inline.
    """
    for page in reader.pages:
        for annot in get_array(page, Annots):
            widget = annot.get_object()
            if _is_widget_annotation(widget) and (
                not isinstance(annot, IndirectObject) or _has_inline_parent(widget)
            ):
                return True

    return False


def _has_inline_parent(obj: DictionaryObject) -> bool:
    """
    Checks whether a field on the `/Parent` chain of an object is stored inline.

    Args:
        obj (DictionaryObject): A widget annotation or field.

    Returns:
        bool: True if a `/Parent` along the chain is not an indirect reference.
    """
    seen = set()
    while get_dictionary(obj, Parent) is not None and id(obj) not in seen:
        seen.add(id(obj))
        if not isinstance(obj.raw_get(Parent), IndirectObject):
            return True
        obj = cast(DictionaryObject, get_dictionary(obj, Parent))

    return False


def share_inline_objects(writer: PdfWriter) -> None:
    """
    Makes inline page widgets and their inline parents shared indirect objects.

    Each widget stored inline in a page's `/Annots` is replaced with a
    reference. Its copy in the field tree is reused when the widget's parent
    `/Kids`, or the AcroForm `/Fields` array for a widget without a parent,
    has an indirect entry that is on no page and has the widget's `/T` and
    `/Rect`, and its `/P` when the widget has one. Each field stored inline in
    the `/Parent` of a page widget or of such a field is replaced the same
    way, reusing an entry of its own container that has its `/T` and lists the
    child in `/Kids`. A reused entry takes the inline object's entries and
    keeps the ones the inline object lacks, such as actions added to the
    field, and a parent keeps its own `/Kids`, so references to the entry,
    such as `/CO` entries or actions, now refer to the object on the page. An
    entry is reused only when it is the one exact copy among the matching
    entries, or the only matching entry. Otherwise the inline object becomes
    a new indirect object, added to its container.

    Args:
        writer (PdfWriter): The PDF writer to update in place.
    """
    acroform = get_dictionary(writer.root_object, AcroForm)
    root_fields = get_array(acroform, Fields) if acroform is not None else ArrayObject()
    on_pages = {
        id(annot.get_object())
        for page in writer.pages
        for annot in get_array(page, Annots)
    }
    claimed = set()

    for page in writer.pages:
        annots = get_array(page, Annots)
        for index, annot in enumerate(annots):
            widget = annot.get_object()
            if not _is_widget_annotation(widget):
                continue
            if not isinstance(annot, IndirectObject):
                annot = _share_inline_widget(
                    writer, widget, root_fields, on_pages, claimed
                )
                annots[index] = annot
            _share_inline_parents(writer, annot, root_fields)


def _share_inline_widget(
    writer: PdfWriter,
    widget: DictionaryObject,
    root_fields: ArrayObject,
    on_pages: set,
    claimed: set,
) -> IndirectObject:
    """
    Returns the reference that replaces an inline page widget.

    Args:
        writer (PdfWriter): The PDF writer that owns the page and field tree.
        widget (DictionaryObject): The inline widget annotation.
        root_fields (ArrayObject): The AcroForm `/Fields` array.
        on_pages (set): The `id` of every annotation listed by a page.
        claimed (set): Object numbers of entries already used for a page
            widget, updated in place.

    Returns:
        IndirectObject: The reused copy, or a new indirect object.
    """
    parent = get_dictionary(widget, Parent)
    container = get_array(parent, Kids) if parent is not None else root_fields
    keys = (T, P) if P in widget else (T,)
    reference = _find_copy(
        container,
        widget,
        lambda copy: (
            _is_widget_annotation(copy)
            and id(copy) not in on_pages
            and all(copy.get(key) == widget.get(key) for key in keys)
            and _get_rect(copy) == _get_rect(widget)
        ),
        claimed,
    )
    if reference is None:
        reference = writer._add_object(widget)  # type: ignore[attr-defined] # noqa: SLF001 # pylint: disable=W0212
        container.append(reference)
    else:
        cast(DictionaryObject, reference.get_object()).update(
            {key: widget.raw_get(key) for key in widget}
        )

    claimed.add(reference.idnum)
    return reference


def _share_inline_parents(
    writer: PdfWriter, child: IndirectObject, root_fields: ArrayObject
) -> None:
    """
    Replaces inline fields along the `/Parent` chain of an indirect object.

    Args:
        writer (PdfWriter): The PDF writer that owns the field tree.
        child (IndirectObject): A page widget, referenced indirectly.
        root_fields (ArrayObject): The AcroForm `/Fields` array.
    """
    obj = cast(DictionaryObject, child.get_object())
    seen = set()
    while (parent := get_dictionary(obj, Parent)) is not None and id(obj) not in seen:
        seen.add(id(obj))
        reference = obj.raw_get(Parent)
        if not isinstance(reference, IndirectObject):
            reference = _share_inline_parent(writer, parent, child, root_fields)
            obj[NameObject(Parent)] = reference
        child = reference
        obj = cast(DictionaryObject, reference.get_object())


def _share_inline_parent(
    writer: PdfWriter,
    parent: DictionaryObject,
    child: IndirectObject,
    root_fields: ArrayObject,
) -> IndirectObject:
    """
    Returns the reference that replaces an inline parent field.

    Args:
        writer (PdfWriter): The PDF writer that owns the field tree.
        parent (DictionaryObject): The inline parent field.
        child (IndirectObject): The child whose `/Parent` it is.
        root_fields (ArrayObject): The AcroForm `/Fields` array.

    Returns:
        IndirectObject: The reused copy, or a new indirect object.
    """
    grandparent = get_dictionary(parent, Parent)
    container = get_array(grandparent, Kids) if grandparent is not None else root_fields
    reference = _find_copy(
        container,
        parent,
        lambda copy: (
            isinstance(copy, DictionaryObject)
            and copy.get(T) == parent.get(T)
            and child in get_array(copy, Kids)
        ),
        set(),
    )
    if reference is None:
        reference = writer._add_object(parent)  # type: ignore[attr-defined] # noqa: SLF001 # pylint: disable=W0212
        container.append(reference)
    else:
        cast(DictionaryObject, reference.get_object()).update(
            {key: parent.raw_get(key) for key in parent if key != Kids}
        )

    return reference


def _find_copy(
    container: ArrayObject,
    obj: DictionaryObject,
    matches: Callable[[object], bool],
    claimed: set,
) -> Optional[IndirectObject]:
    """
    Finds the entry of a container that is the copy of an inline object.

    Args:
        container (ArrayObject): The `/Kids` or `/Fields` array to search.
        obj (DictionaryObject): The inline object.
        matches (Callable[[object], bool]): Decides which resolved entries
            match the inline object.
        claimed (set): Object numbers of entries that cannot be used.

    Returns:
        Optional[IndirectObject]: The only matching entry equal to `obj`, or
            the only matching entry when none is equal to it, or None when
            the match is not unique.
    """
    found = [
        entry
        for entry in container
        if isinstance(entry, IndirectObject)
        and entry.idnum not in claimed
        and matches(entry.get_object())
    ]
    exact = [entry for entry in found if entry.get_object() == obj]
    candidates = exact or found

    return candidates[0] if len(candidates) == 1 else None


def _get_rect(annot: DictionaryObject) -> list:
    """
    Gets the `/Rect` of an annotation as numbers.

    Args:
        annot (DictionaryObject): The annotation.

    Returns:
        list: The rectangle's coordinates, or an empty list without one.
    """
    return [float(each.get_object()) for each in get_array(annot, Rect)]


def update_widget_keys(
    template: bytes,
    widgets: Dict[str, WIDGET_TYPES],
    old_keys: List[str],
    new_keys: List[str],
    indices: List[int],
) -> bytes:
    """
    Updates the keys of widgets in a PDF template.

    This function updates queued widget names in a PDF template based on
    parallel lists of old keys, new keys, and occurrence indices. Non-radio
    widgets use `indices` to disambiguate duplicate field names. Radio widgets
    update every annotation in the radio group.

    Args:
        template (bytes): The PDF template to update.
        widgets (Dict[str, WIDGET_TYPES]): A dictionary of widgets in the template.
        old_keys (List[str]): A list of the old widget keys to be replaced.
        new_keys (List[str]): A list of the new widget keys to replace the old keys.
        indices (List[int]): A list of indices to handle the case where multiple widgets have the same name.

    Returns:
        bytes: The updated PDF template as a byte stream.
    """
    out = PdfWriter(BytesIO(template))

    _apply_widget_key_updates(out, widgets, old_keys, new_keys, indices)

    with BytesIO() as f:
        out.write(f)
        f.seek(0)
        return f.read()


def _apply_widget_key_updates(
    writer: PdfWriter,
    widgets: Dict[str, WIDGET_TYPES],
    old_keys: List[str],
    new_keys: List[str],
    indices: List[int],
) -> None:
    """
    Applies queued widget key updates to matching annotations.

    The update queue is converted into a lookup keyed by old widget name, then
    each annotation is checked against that lookup as pages are traversed.
    Non-radio widgets honor the requested occurrence index, while radio widgets
    update every annotation in the radio group.

    Args:
        writer (PdfWriter): The PDF writer object.
        widgets (Dict[str, WIDGET_TYPES]): A dictionary of widgets in the template.
        old_keys (List[str]): The old widget keys to replace.
        new_keys (List[str]): The new widget keys to apply.
        indices (List[int]): Widget occurrence indices for duplicate field names.
    """
    updates = {old_key: (new_keys[i], indices[i]) for i, old_key in enumerate(old_keys)}
    trackers = {}

    for page in writer.pages:
        for annot in page.get(Annots, []):
            annot = cast(DictionaryObject, annot.get_object())
            key = get_widget_key(annot.get_object(), False)

            if key not in updates:
                continue

            widget = widgets.get(key)
            if widget is not None:
                trackers[key] = trackers.get(key, -1) + 1
                new_key, index = updates[key]
                if not isinstance(widget, Radio) and trackers[key] != index:
                    continue

                update_annotation_name(annot, new_key)
