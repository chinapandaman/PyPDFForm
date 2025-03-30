# -*- coding: utf-8 -*-
"""Contains utility helpers."""

from collections.abc import Callable
from io import BytesIO
from secrets import choice
from string import ascii_letters, digits, punctuation
from typing import Any, BinaryIO, List, Union

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject
from reportlab.lib.colors import CMYKColor, Color

from .constants import (BUTTON_STYLES, DEFAULT_CHECKBOX_STYLE, DEFAULT_FONT,
                        DEFAULT_FONT_COLOR, DEFAULT_FONT_SIZE,
                        DEFAULT_RADIO_STYLE, PREVIEW_FONT_COLOR,
                        UNIQUE_SUFFIX_LENGTH, WIDGET_TYPES)
from .middleware.checkbox import Checkbox
from .middleware.radio import Radio
from .middleware.text import Text


def stream_to_io(stream: bytes) -> BinaryIO:
    """Converts a byte stream to a binary io object."""

    result = BytesIO()
    result.write(stream)
    result.seek(0)

    return result


def handle_color(color: Union[list, ArrayObject]) -> Union[Color, CMYKColor, None]:
    """Converts a color array to an RGB or CMYK color."""

    result = None

    if len(color) == 1:
        result = CMYKColor(black=1 - color[0])
    elif len(color) == 3:
        result = Color(red=color[0], green=color[1], blue=color[2])
    elif len(color) == 4:
        result = CMYKColor(
            cyan=color[0], magenta=color[1], yellow=color[2], black=color[3]
        )

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
        DEFAULT_CHECKBOX_STYLE if type(widget) is Checkbox else DEFAULT_RADIO_STYLE
    )

    return new_widget


def preview_widget_to_draw(widget: WIDGET_TYPES, with_preview_text: bool) -> Text:
    """Converts a widget to a preview text widget."""

    new_widget = Text(
        name=widget.name,
        value="{" + f" {widget.name} " + "}" if with_preview_text else None,
    )
    new_widget.font = DEFAULT_FONT
    new_widget.font_size = DEFAULT_FONT_SIZE
    new_widget.font_color = PREVIEW_FONT_COLOR
    new_widget.preview = with_preview_text
    new_widget.border_color = handle_color([0, 0, 0])
    new_widget.border_width = 1
    new_widget.render_widget = True

    return new_widget


def remove_all_widgets(pdf: bytes) -> bytes:
    """Removes all widgets from a PDF form."""

    pdf_file = PdfReader(stream_to_io(pdf))
    result_stream = BytesIO()
    writer = PdfWriter()
    for page in pdf_file.pages:
        if page.annotations:
            page.annotations.clear()
        writer.add_page(page)

    writer.write(result_stream)
    result_stream.seek(0)
    return result_stream.read()


def get_page_streams(pdf: bytes) -> List[bytes]:
    """Returns a list of streams where each is a page of the input PDF."""

    pdf_file = PdfReader(stream_to_io(pdf))
    result = []

    for page in pdf_file.pages:
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
    pdf_file = PdfReader(stream_to_io(pdf))
    other_file = PdfReader(stream_to_io(other))
    result = BytesIO()

    for page in pdf_file.pages:
        output.add_page(page)
    for page in other_file.pages:
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
                if isinstance(pattern[key], tuple):
                    result = value in pattern[key]
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


def extract_widget_property(
    widget: Union[dict, DictionaryObject],
    patterns: list,
    default_value: Any,
    func_before_return: Union[Callable, None],
) -> Any:
    """Returns a property value given a PDF widget dict and a pattern."""

    result = default_value

    for pattern in patterns:
        value = traverse_pattern(pattern, widget)
        if value:
            result = func_before_return(value) if func_before_return else value
            break

    return result


def generate_unique_suffix() -> str:
    """Generates a unique suffix string for widgets during form merging."""

    return "".join(
        [
            choice(ascii_letters + digits + punctuation.replace("-", ""))
            for _ in range(UNIQUE_SUFFIX_LENGTH)
        ]
    )
