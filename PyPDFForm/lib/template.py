# -*- coding: utf-8 -*-
"""
Module for handling PDF form templates.

This module provides functionalities to extract, build, and update widgets
in PDF form templates. It leverages the pypdf library for PDF manipulation
and defines specific patterns for identifying and constructing different
types of widgets.
"""

from copy import deepcopy
from functools import lru_cache, wraps
from io import BytesIO
from typing import Dict, List, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, NameObject

from .annotations import AnnotationTypes
from .constants import COMB, MULTILINE, READ_ONLY, REQUIRED, Annots
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
from .utils import extract_widget_property, find_pattern_match


def acroform_fields_dirty(method):
    """
    Marks methods that rewrite page widget annotations without maintaining root fields.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        if self.widgets:
            self._mark_acroform_fields_dirty()
        return result

    return wrapper


@lru_cache(maxsize=128)
def get_metadata(pdf: bytes) -> dict:
    """
    Retrieves the metadata of a PDF.

    Args:
        pdf (bytes): The PDF stream to extract metadata from.

    Returns:
        dict: A dictionary containing the PDF's metadata.
    """
    if not pdf:
        return {}

    reader = PdfReader(BytesIO(pdf))
    return reader.metadata or {}


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


@lru_cache(maxsize=128)
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


@lru_cache(maxsize=128)
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


def create_annotations(
    template: bytes,
    annotations: List[AnnotationTypes],
) -> bytes:
    """
    Creates and adds annotations to a PDF template.

    This function takes a PDF template and a list of annotation objects, builds
    their PDF dictionaries, and appends them to the `/Annots` array for each
    target page. Existing annotations are preserved, and annotation page numbers
    are 1-based.

    Args:
        template (bytes): The PDF template to add annotations to.
        annotations (List[AnnotationTypes]): A list of annotation objects to be
            added to the PDF.

    Returns:
        bytes: The updated PDF stream with the added annotations.
    """
    writer = PdfWriter(BytesIO(template))
    annotations_by_page = _group_annotations_by_page(annotations)

    for i, page in enumerate(writer.pages):
        page_num = i + 1
        if page_num not in annotations_by_page:
            continue

        page_annotations = ArrayObject([])
        for annotation in annotations_by_page[page_num]:
            page_annotations.append(annotation.get_specific_properties())

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
    Removes specific widgets from a PDF by their keys.

    This function removes any widget annotation whose key matches one of the
    provided keys. If no keys are provided, the original PDF stream is returned
    unchanged.

    Args:
        pdf (bytes): The PDF stream to remove widgets from.
        keys (List[str]): A list of widget keys to remove.
        use_full_widget_name (bool): Whether to match widgets by their full
            names, including parent names.

    Returns:
        bytes: The updated PDF stream with the matching widgets removed.
    """
    if not keys:
        return pdf

    key_set = set(keys)
    writer = PdfWriter(BytesIO(pdf))

    for page in writer.pages:
        needs_update = False
        page_annots = ArrayObject([])

        for annot in page.get(Annots, []):
            annot = cast(DictionaryObject, annot.get_object())
            key = get_widget_key(annot.get_object(), use_full_widget_name)
            if key not in key_set:
                page_annots.append(annot)
            else:
                needs_update = True

        if needs_update:
            page[NameObject(Annots)] = page_annots

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
    pdf = PdfReader(BytesIO(template))
    out = PdfWriter()
    out.append(pdf)

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
