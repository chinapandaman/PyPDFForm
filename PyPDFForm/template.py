# -*- coding: utf-8 -*-
"""
Module for handling PDF form templates.

This module provides functionalities to extract, build, and update widgets
in PDF form templates. It leverages the pypdf library for PDF manipulation
and defines specific patterns for identifying and constructing different
types of widgets.
"""

from functools import lru_cache
from io import BytesIO
from typing import Dict, List, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject,
                           NameObject, TextStringObject)

from .annotations import AnnotationTypes
from .constants import (COMB, MULTILINE, READ_ONLY, REQUIRED, WIDGET_TYPES,
                        Annot, Annots, Contents, Rect, Subtype, Type)
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.radio import Radio
from .middleware.text import Text
from .patterns import (WIDGET_DESCRIPTION_PATTERNS, WIDGET_TYPE_PATTERNS,
                       check_field_flag, get_checkbox_value,
                       get_dropdown_choices, get_dropdown_value,
                       get_field_hidden, get_field_rect, get_radio_value,
                       get_text_field_alignment, get_text_field_max_length,
                       get_text_value, get_widget_key, update_annotation_name)
from .utils import extract_widget_property, find_pattern_match, stream_to_io


@lru_cache
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

    reader = PdfReader(stream_to_io(pdf))
    return reader.metadata or {}


def set_metadata(pdf: bytes, metadata: dict) -> bytes:
    """
    Sets the metadata of a PDF.

    Args:
        pdf (bytes): The PDF stream to set metadata for.
        metadata (dict): A dictionary containing the metadata to be set.

    Returns:
        bytes: The updated PDF stream with the new metadata.
    """
    reader = PdfReader(stream_to_io(pdf))
    writer = PdfWriter(clone_from=reader)
    writer.add_metadata(metadata)

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


def build_widgets(
    pdf_stream: bytes,
    use_full_widget_name: bool,
) -> Dict[str, WIDGET_TYPES]:
    """
    Builds a dictionary of widgets from a PDF stream.

    This function parses a PDF stream to identify and construct widgets
    present in the PDF form. It iterates through each page and its annotations,
    extracting widget properties such as key, description, max length (for text fields),
    and choices (for dropdowns). The constructed widgets are stored in a dictionary
    where the keys are the widget keys and the values are the widget objects.

    Args:
        pdf_stream (bytes): The PDF stream to parse.
        use_full_widget_name (bool): Whether to use the full widget name
            (including parent names) as the widget key.

    Returns:
        Dict[str, WIDGET_TYPES]: A dictionary of widgets, where keys are widget
            keys and values are widget objects.
    """
    results = {}

    for widgets in get_widgets_by_page(pdf_stream).values():
        for widget in widgets:
            _process_widget(widget, use_full_widget_name, results)

    return results


def _process_widget(
    widget: dict, use_full_widget_name: bool, results: Dict[str, WIDGET_TYPES]
) -> None:
    """
    Processes a single widget and adds it to the results dictionary.

    Args:
        widget (dict): The widget dictionary from the PDF.
        use_full_widget_name (bool): Whether to use the full widget name.
        results (Dict[str, WIDGET_TYPES]): The dictionary of widgets being built.
    """
    key = get_widget_key(widget, use_full_widget_name)
    _widget = construct_widget(widget, key)
    if _widget is not None:
        _populate_common_properties(widget, _widget)

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


def _populate_common_properties(widget: dict, _widget: WIDGET_TYPES) -> None:
    """
    Populates common properties for a widget.

    Args:
        widget (dict): The widget dictionary from the PDF.
        _widget (WIDGET_TYPES): The widget object to populate.
    """
    # widget property extractions don't trigger hooks in this function
    _widget.__dict__["tooltip"] = extract_widget_property(
        widget, WIDGET_DESCRIPTION_PATTERNS, None, str
    )
    _widget.__dict__["readonly"] = check_field_flag(widget, READ_ONLY)
    _widget.__dict__["required"] = check_field_flag(widget, REQUIRED)
    _widget.__dict__["hidden"] = get_field_hidden(widget)

    _widget.x, _widget.y, _widget.width, _widget.height = get_field_rect(widget)


def _populate_text_properties(widget: dict, _widget: Text) -> None:
    """
    Populates properties specific to text widgets.

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

    Args:
        widget (dict): The widget dictionary from the PDF.
        key (str): The widget key.
        _widget (Radio): The radio widget object.
        results (Dict[str, WIDGET_TYPES]): The dictionary of widgets being built.
    """
    field_rect = get_field_rect(widget)

    if key not in results:
        _widget.x = []
        _widget.y = []
        _widget.width = []
        _widget.height = []
        results[key] = _widget

    radio = cast(Radio, results[key])
    # for schema
    radio.number_of_options += 1

    if isinstance(radio.x, list):
        radio.x.append(field_rect[0])
    if isinstance(radio.y, list):
        radio.y.append(field_rect[1])
    if isinstance(radio.width, list):
        radio.width.append(field_rect[2])
    if isinstance(radio.height, list):
        radio.height.append(field_rect[3])

    if get_radio_value(widget):
        radio.value = radio.number_of_options - 1


@lru_cache()
def get_widgets_by_page(pdf: bytes) -> Dict[int, List[dict]]:
    """
    Retrieves widgets from a PDF stream, organized by page number.

    This function parses a PDF stream and extracts all the widgets (annotations)
    present on each page. It returns a dictionary where the keys are the page
    numbers and the values are lists of widget dictionaries.

    Args:
        pdf (bytes): The PDF stream to parse.

    Returns:
        Dict[int, List[dict]]: A dictionary where keys are page numbers (1-indexed)
            and values are lists of widget dictionaries.
    """
    pdf_file = PdfReader(stream_to_io(pdf))

    result = {}

    for i, page in enumerate(pdf_file.pages):
        result[i + 1] = _get_widgets_on_page(page)

    return result


def _get_widgets_on_page(page) -> List[dict]:
    """
    Retrieves widgets from a single PDF page.

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
    and constructs the corresponding widget object.

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


def _create_annotation_object(annotation: AnnotationTypes) -> DictionaryObject:
    """
    Creates a PDF dictionary object for an annotation.

    Args:
        annotation (AnnotationTypes): The annotation object to convert.

    Returns:
        DictionaryObject: The PDF dictionary object representing the annotation.
    """
    annot = DictionaryObject(
        {
            NameObject(Type): NameObject(Annot),
            NameObject(Subtype): NameObject(getattr(annotation, "_annotation_type")),
            NameObject(Rect): ArrayObject(
                [
                    FloatObject(annotation.x),
                    FloatObject(annotation.y),
                    FloatObject(annotation.x + annotation.width),
                    FloatObject(annotation.y + annotation.height),
                ]
            ),
            NameObject(Contents): TextStringObject(annotation.contents),
        }
    )
    annot.update(**annotation.get_specific_properties())
    return annot


def create_annotations(
    template: bytes,
    annotations: List[AnnotationTypes],
) -> bytes:
    """
    Creates and adds annotations to a PDF template.

    This function takes a PDF template and a list of annotation objects, and
    renders each annotation onto its specified page in the PDF. It supports
    various annotation types defined in the `PyPDFForm.annotations` package.

    Args:
        template (bytes): The PDF template to add annotations to.
        annotations (List[AnnotationTypes]): A list of annotation objects to be
            added to the PDF.

    Returns:
        bytes: The updated PDF stream with the added annotations.
    """
    reader = PdfReader(stream_to_io(template))
    writer = PdfWriter(clone_from=reader)

    annotations_by_page = _group_annotations_by_page(annotations)

    for i, page in enumerate(writer.pages):
        page_num = i + 1
        if page_num not in annotations_by_page:
            continue

        page_annotations = ArrayObject([])
        for annotation in annotations_by_page[page_num]:
            page_annotations.append(_create_annotation_object(annotation))

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

    This function updates the keys of widgets in a PDF template based on the provided old keys and new keys.
    It iterates through each page and annotation, finds the widgets with the old keys, and updates their names with the corresponding new keys.
    The `indices` parameter is used when multiple widgets have the same name, to differentiate which one to update.

    Args:
        template (bytes): The PDF template to update.
        widgets (Dict[str, WIDGET_TYPES]): A dictionary of widgets in the template.
        old_keys (List[str]): A list of the old widget keys to be replaced.
        new_keys (List[str]): A list of the new widget keys to replace the old keys.
        indices (List[int]): A list of indices to handle the case where multiple widgets have the same name.

    Returns:
        bytes: The updated PDF template as a byte stream.
    """
    pdf = PdfReader(stream_to_io(template))
    out = PdfWriter()
    out.append(pdf)

    for i, old_key in enumerate(old_keys):
        _update_single_widget_key(out, widgets, old_key, new_keys[i], indices[i])

    with BytesIO() as f:
        out.write(f)
        f.seek(0)
        return f.read()


def _update_single_widget_key(
    writer: PdfWriter,
    widgets: Dict[str, WIDGET_TYPES],
    old_key: str,
    new_key: str,
    index: int,
) -> None:
    """
    Updates a single widget key in a PDF template.

    Args:
        writer (PdfWriter): The PDF writer object.
        widgets (Dict[str, WIDGET_TYPES]): A dictionary of widgets in the template.
        old_key (str): The old widget key to be replaced.
        new_key (str): The new widget key to replace the old key.
        index (int): The index of the widget to update if multiple widgets have the same name.
    """
    tracker = -1
    for page in writer.pages:
        for annot in page.get(Annots, []):
            annot = cast(DictionaryObject, annot.get_object())
            key = get_widget_key(annot.get_object(), False)

            widget = widgets.get(key)
            if widget is None or old_key != key:
                continue

            tracker += 1
            if not isinstance(widget, Radio) and tracker != index:
                continue

            update_annotation_name(annot, new_key)
