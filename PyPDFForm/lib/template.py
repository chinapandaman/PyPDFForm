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
from typing import Dict, List, Optional, Tuple, cast

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
    COMB,
    JS,
    MULTILINE,
    READ_ONLY,
    REQUIRED,
    AcroForm,
    Annots,
    Dest,
    JavaScript,
    OpenAction,
    S,
    Title,
)
from .middleware import WIDGET_TYPES
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.radio import Radio
from .middleware.text import Text
from .patterns import (
    check_field_flag,
    get_checkbox_value,
    get_dropdown_choices,
    get_dropdown_value,
    get_field_hidden,
    get_field_rect,
    get_field_tooltip,
    get_radio_value,
    get_text_field_alignment,
    get_text_field_max_length,
    get_text_field_style,
    get_text_value,
    get_widget_key,
    get_widget_type,
    update_annotation_name,
)
from .utils import get_dictionary


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
    radios = {}
    reader = PdfReader(BytesIO(pdf_stream))
    acroform = get_dictionary(reader.root_object, AcroForm)

    for page_num, page in enumerate(reader.pages, start=1):
        for index, (widget, annot) in enumerate(_get_widget_annotations(page)):
            _process_widget(
                widget,
                get_widget_key(annot, use_full_widget_name),
                page_num,
                results,
                radios,
                acroform,
                index,
            )

    return results


def get_widget_positions(pdf_stream: bytes) -> Dict[str, tuple]:
    """
    Gets where the widget that each short key gives access to is in a PDF.

    The position is the page number and the index of the widget among the
    widgets on that page, which renaming doesn't change. For a radio group, it
    is the position of its first option.

    Args:
        pdf_stream (bytes): The PDF stream to parse.

    Returns:
        Dict[str, tuple]: The `(page number, index)` of each key's widget.
    """
    if not pdf_stream:
        return {}

    return {
        key: widget.__dict__["_position"]
        for key, widget in _build_widget_cache(pdf_stream, False).items()
    }


def _process_widget(
    widget: dict,
    key: str,
    page_number: int,
    results: Dict[str, WIDGET_TYPES],
    radios: Dict[str, Radio],
    acroform: Optional[DictionaryObject],
    index: int,
) -> None:
    """
    Processes a single widget and adds it to the results dictionary.

    Common geometry and flags are populated for every recognized widget. Text,
    checkbox, dropdown, and radio widgets then get type-specific state. Radio
    annotations that share a key are aggregated into one middleware object with
    per-option geometry and a selected option index. A widget replaces an
    earlier one with its key, so the key gives access to the last one.

    Args:
        widget (dict): The widget dictionary from the PDF.
        key (str): The widget's key, computed from the PDF's own annotation,
            as `get_widget_key` requires.
        page_number (int): The 1-indexed page number the widget appears on.
        results (Dict[str, WIDGET_TYPES]): The dictionary of widgets being built.
        radios (Dict[str, Radio]): The radio groups being built, by key, kept
            when a widget of another type replaces them in `results`.
        acroform (Optional[DictionaryObject]): The AcroForm dictionary, whose
            default appearance text fields and dropdowns can inherit.
        index (int): The index of the widget among the widgets on its page.
    """
    _widget = construct_widget(widget, key)
    if _widget is not None:
        # which widget the key gives access to, as `get_widget_positions` reads it
        _widget.__dict__["_position"] = (page_number, index)
        _populate_common_properties(widget, page_number, _widget)

        if isinstance(_widget, (Text, Dropdown)):
            _populate_style_properties(widget, _widget, acroform)

        if isinstance(_widget, Text):
            _populate_text_properties(widget, _widget)

        if type(_widget) is Checkbox:
            _widget.value = get_checkbox_value(widget)
            # the value the PDF holds, which filling doesn't write again
            _widget.__dict__["_pdf_value"] = _widget.value

        if isinstance(_widget, Dropdown):
            _populate_dropdown_properties(widget, _widget)

        if isinstance(_widget, Radio):
            _handle_radio_widget(widget, key, _widget, radios)
            results[key] = radios[key]
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
    _widget.__dict__["tooltip"] = get_field_tooltip(widget)
    _widget.__dict__["readonly"] = check_field_flag(widget, READ_ONLY)
    _widget.__dict__["required"] = check_field_flag(widget, REQUIRED)
    _widget.__dict__["hidden"] = get_field_hidden(widget)

    (
        _widget.__dict__["x"],
        _widget.__dict__["y"],
        _widget.__dict__["width"],
        _widget.__dict__["height"],
    ) = get_field_rect(widget)


def _populate_style_properties(
    widget: dict, _widget: Text | Dropdown, acroform: Optional[DictionaryObject]
) -> None:
    """
    Populates the font, font size, and font color of a text field or dropdown.

    They are read from the default appearance that a change to them edits, as
    `get_text_field_style` describes, and assigned directly so loading
    existing PDF state does not trigger write hooks.

    Args:
        widget (dict): The widget dictionary from the PDF.
        _widget (Text | Dropdown): The widget object to populate.
        acroform (Optional[DictionaryObject]): The AcroForm dictionary.
    """
    style = get_text_field_style(widget, acroform)
    _widget.__dict__["font"] = style.font
    _widget.__dict__["font_size"] = style.font_size
    _widget.__dict__["font_color"] = style.font_color


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
    widget: dict, key: str, _widget: Radio, radios: Dict[str, Radio]
) -> None:
    """
    Handles the logic for radio widgets, including aggregating multiple options.

    Each radio annotation contributes one option to a shared `Radio` object. The
    method stores per-option rectangles as lists, increments the option count for
    schema generation, and records the selected option index when the annotation
    is currently selected. The group is kept by key apart from the other
    widgets, so options separated by a widget of another type with the same
    key, such as a checkbox with the same short name, stay in one group.

    Args:
        widget (dict): The widget dictionary from the PDF.
        key (str): The widget key.
        _widget (Radio): The radio widget object.
        radios (Dict[str, Radio]): The radio groups being built, by key.
    """
    field_rect = get_field_rect(widget)

    if key not in radios:
        _widget.__dict__["x"] = []
        _widget.__dict__["y"] = []
        _widget.__dict__["width"] = []
        _widget.__dict__["height"] = []
        radios[key] = _widget

    radio = radios[key]
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
    return [widget for widget, _ in _get_widget_annotations(page)]


def _get_widget_annotations(page) -> List[Tuple[dict, DictionaryObject]]:
    """
    Retrieves the widgets of a single PDF page with their annotations.

    Each widget is a plain dictionary copied from the page annotation, as
    `_get_widgets_on_page` returns it, and is paired with the annotation
    itself, which is the PDF's own object that `get_widget_key` requires.

    Args:
        page: The PDF page object.

    Returns:
        List[Tuple[dict, DictionaryObject]]: The widget dictionaries found on
            the page, each with its annotation.
    """
    annotations = page.annotations
    result = []
    if annotations:
        for reference in annotations:
            annot = reference.get_object()
            widget = dict(annot)
            if _is_widget(widget):
                result.append((widget, annot))
    return result


def _is_widget(widget: dict) -> bool:
    """
    Checks if a dictionary represents a valid widget.

    A widget is considered valid when `get_widget_type` finds its type.

    Args:
        widget (dict): The dictionary to check.

    Returns:
        bool: True if the dictionary represents a widget, False otherwise.
    """
    return get_widget_type(widget) is not None


def construct_widget(widget: dict, key: str) -> WIDGET_TYPES | None:
    """
    Constructs a widget object based on the widget dictionary and key.

    This function determines the type of widget with `get_widget_type` and
    constructs the corresponding middleware widget object using the supplied
    key as its name.

    Args:
        widget (dict): The widget dictionary to construct the object from.
        key (str): The key of the widget.

    Returns:
        WIDGET_TYPES | None: The constructed widget object, or None
            if the widget type is not recognized.
    """
    _type = get_widget_type(widget)
    return _type(key) if _type is not None else None


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
