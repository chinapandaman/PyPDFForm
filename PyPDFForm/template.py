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
from typing import Dict, List, Tuple, Union, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject

from .constants import WIDGET_TYPES, Annots, MaxLen, Parent, T
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.radio import Radio
from .middleware.text import Text
from .patterns import (DROPDOWN_CHOICE_PATTERNS, WIDGET_DESCRIPTION_PATTERNS,
                       WIDGET_KEY_PATTERNS, WIDGET_TYPE_PATTERNS,
                       get_checkbox_value, get_dropdown_value, get_radio_value,
                       get_text_field_multiline, get_text_value,
                       update_annotation_name)
from .utils import extract_widget_property, find_pattern_match, stream_to_io


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
            key = get_widget_key(widget, use_full_widget_name)
            _widget = construct_widget(widget, key)
            if _widget is not None:
                _widget.__dict__["tooltip"] = extract_widget_property(
                    widget, WIDGET_DESCRIPTION_PATTERNS, None, str
                )

                if isinstance(_widget, Text):
                    # mostly for schema for now
                    # doesn't trigger hook
                    _widget.__dict__["max_length"] = get_text_field_max_length(widget)
                    _widget.__dict__["multiline"] = get_text_field_multiline(widget)
                    get_text_value(widget, _widget)

                if type(_widget) is Checkbox:
                    _widget.value = get_checkbox_value(widget)

                if isinstance(_widget, Dropdown):
                    # actually used for filling value
                    # doesn't trigger hook
                    _widget.__dict__["choices"] = get_dropdown_choices(widget)
                    get_dropdown_value(widget, _widget)

                if isinstance(_widget, Radio):
                    if key not in results:
                        results[key] = _widget

                    # for schema
                    results[key].number_of_options += 1

                    if get_radio_value(widget):
                        results[key].value = results[key].number_of_options - 1
                    continue

                results[key] = _widget

    return results


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
        widgets = page.annotations
        result[i + 1] = []
        if widgets:
            for widget in widgets:
                widget = dict(widget.get_object())
                for each in WIDGET_TYPE_PATTERNS:
                    patterns = each[0]
                    check = True
                    for pattern in patterns:
                        check = check and find_pattern_match(pattern, widget)
                    if check:
                        result[i + 1].append(widget)
                        break

    return result


def get_widget_key(widget: dict, use_full_widget_name: bool) -> str:
    """
    Extracts the widget key from a widget dictionary.

    This function extracts the widget key from a widget dictionary based on
    predefined patterns. If `use_full_widget_name` is True, it recursively
    constructs the full widget name by concatenating the parent widget keys.

    Args:
        widget (dict): The widget dictionary to extract the key from.
        use_full_widget_name (bool): Whether to use the full widget name
            (including parent names) as the widget key.

    Returns:
        str: The extracted widget key.
    """
    if not use_full_widget_name:
        return extract_widget_property(widget, WIDGET_KEY_PATTERNS, None, str)

    key = widget.get(T)
    if (
        Parent in widget
        and T in widget[Parent].get_object()
        and widget[Parent].get_object()[T] != key  # sejda case
    ):
        if key is None:
            return get_widget_key(widget[Parent].get_object(), use_full_widget_name)

        return (
            f"{get_widget_key(widget[Parent].get_object(), use_full_widget_name)}.{key}"
        )

    return key or ""


def construct_widget(widget: dict, key: str) -> Union[WIDGET_TYPES, None]:
    """
    Constructs a widget object based on the widget dictionary and key.

    This function determines the type of widget based on predefined patterns
    and constructs the corresponding widget object.

    Args:
        widget (dict): The widget dictionary to construct the object from.
        key (str): The key of the widget.

    Returns:
        Union[WIDGET_TYPES, None]: The constructed widget object, or None
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


def get_text_field_max_length(widget: dict) -> Union[int, None]:
    """
    Extracts the maximum length of a text field from a widget dictionary.

    Args:
        widget (dict): The widget dictionary to extract the max length from.

    Returns:
        Union[int, None]: The maximum length of the text field, or None
            if the max length is not specified.
    """
    return int(widget[MaxLen]) or None if MaxLen in widget else None


def get_dropdown_choices(widget: dict) -> Union[Tuple[str, ...], None]:
    """
    Extracts the choices from a dropdown widget dictionary.

    This function extracts the choices from a dropdown widget dictionary.

    Args:
        widget (dict): The widget dictionary to extract the choices from.

    Returns:
        Union[Tuple[str, ...], None]: A tuple of strings representing the choices in the dropdown, or None if the choices are not specified.
    """
    return tuple(
        (
            each.get_object()
            if isinstance(each.get_object(), str)
            else str(each.get_object()[1])
        )
        for each in extract_widget_property(
            widget, DROPDOWN_CHOICE_PATTERNS, None, None
        )
    )


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
        index = indices[i]
        new_key = new_keys[i]
        tracker = -1
        for page in out.pages:
            for annot in page.get(Annots, []):
                annot = cast(DictionaryObject, annot.get_object())
                key = get_widget_key(annot.get_object(), False)

                widget = widgets.get(key)
                if widget is None:
                    continue

                if old_key != key:
                    continue

                tracker += 1
                if not isinstance(widget, Radio) and tracker != index:
                    continue

                update_annotation_name(annot, new_key)

    with BytesIO() as f:
        out.write(f)
        f.seek(0)
        return f.read()
