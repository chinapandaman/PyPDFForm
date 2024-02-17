# -*- coding: utf-8 -*-
"""Contains utility helpers."""

from io import BytesIO
from typing import BinaryIO, List, Union

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject

from .constants import (BUTTON_STYLES, DEFAULT_CHECKBOX_STYLE, DEFAULT_FONT,
                        DEFAULT_FONT_COLOR, DEFAULT_FONT_SIZE,
                        DEFAULT_RADIO_STYLE, PREVIEW_FONT_COLOR, WIDGET_TYPES)
from .middleware.checkbox import Checkbox
from .middleware.radio import Radio
from .middleware.text import Text


def stream_to_io(stream: bytes) -> BinaryIO:
    """Converts a byte stream to a binary io object."""

    result = BytesIO()
    result.write(stream)
    result.seek(0)

    return result


def checkbox_radio_to_draw(
    widget: Union[Checkbox, Radio], font_size: Union[float, int]
) -> Text:
    """Converts a checkbox/radio widget to a drawable text widget."""

    new_widget = Text(
        name=widget.name,
        value="",
    )
    new_widget.font = DEFAULT_FONT
    new_widget.font_size = font_size
    new_widget.font_color = DEFAULT_FONT_COLOR
    new_widget.value = BUTTON_STYLES.get(widget.button_style) or (
        DEFAULT_CHECKBOX_STYLE if isinstance(widget, Checkbox) else DEFAULT_RADIO_STYLE
    )

    return new_widget


def preview_widget_to_draw(widget: WIDGET_TYPES) -> Text:
    """Converts a widget to a preview text widget."""

    new_widget = Text(
        name=widget.name,
        value="{" + f" {widget.name} " + "}",
    )
    new_widget.font = DEFAULT_FONT
    new_widget.font_size = DEFAULT_FONT_SIZE
    new_widget.font_color = PREVIEW_FONT_COLOR
    new_widget.preview = True

    return new_widget


def remove_all_widgets(pdf: bytes) -> bytes:
    """Removes all widgets from a PDF form."""

    pdf = PdfReader(stream_to_io(pdf))
    result_stream = BytesIO()
    writer = PdfWriter()
    for page in pdf.pages:
        if page.annotations:
            page.annotations.clear()
        writer.add_page(page)

    writer.write(result_stream)
    result_stream.seek(0)
    return result_stream.read()


def get_page_streams(pdf: bytes) -> List[bytes]:
    """Returns a list of streams where each is a page of the input PDF."""

    pdf = PdfReader(stream_to_io(pdf))
    result = []

    for page in pdf.pages:
        writer = PdfWriter()
        writer.add_page(page)
        with BytesIO() as f:
            writer.write(f)
            f.seek(0)
            result.append(f.read())

    return result


def merge_two_pdfs(pdf: bytes, other: bytes) -> bytes:
    """Merges two PDFs into one PDF."""

    output = PdfWriter()
    pdf = PdfReader(stream_to_io(pdf))
    other = PdfReader(stream_to_io(other))
    result = BytesIO()

    for page in pdf.pages:
        output.add_page(page)
    for page in other.pages:
        output.add_page(page)

    output.write(result)
    result.seek(0)
    return result.read()


def find_pattern_match(pattern: dict, widget: Union[dict, DictionaryObject]) -> bool:
    """Checks if a PDF dict pattern exists in a PDF widget."""

    for key, value in widget.items():
        result = False
        if key in pattern:
            value = value.get_object()
            if isinstance(pattern[key], dict) and isinstance(
                value, (dict, DictionaryObject)
            ):
                result = find_pattern_match(pattern[key], value)
            else:
                result = pattern[key] == value
        if result:
            return result
    return False


def traverse_pattern(
    pattern: dict, widget: Union[dict, DictionaryObject]
) -> Union[str, list, None]:
    """Traverses down a PDF dict pattern and find the value."""

    for key, value in widget.items():
        result = None
        if key in pattern:
            value = value.get_object()
            if isinstance(pattern[key], dict) and isinstance(
                value, (dict, DictionaryObject)
            ):
                result = traverse_pattern(pattern[key], value)
            else:
                if pattern[key] is True and value:
                    return value
        if result:
            return result
    return None
