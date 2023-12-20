# -*- coding: utf-8 -*-
"""Contains utility helpers."""

from io import BytesIO
from typing import List, Union

from pdfrw import PdfDict, PdfReader, PdfWriter

from ..middleware.checkbox import Checkbox
from ..middleware.constants import ELEMENT_TYPES
from ..middleware.radio import Radio
from ..middleware.text import Text
from .constants import (ANNOTATION_KEY, CHECKBOX_TO_DRAW, DEFAULT_FONT,
                        DEFAULT_FONT_COLOR, DEFAULT_FONT_SIZE,
                        PREVIEW_FONT_COLOR, RADIO_TO_DRAW)


def generate_stream(pdf: PdfReader) -> bytes:
    """Generates new stream for manipulated PDF form."""

    result_stream = BytesIO()

    PdfWriter().write(result_stream, pdf)
    result_stream.seek(0)

    result = result_stream.read()
    result_stream.close()

    return result


def checkbox_radio_to_draw(
    element: Union[Checkbox, Radio], font_size: Union[float, int]
) -> Text:
    """Converts a checkbox/radio element to a drawable text element."""

    new_element = Text(
        element_name=element.name,
        element_value="",
    )
    new_element.font = DEFAULT_FONT
    new_element.font_size = font_size
    new_element.font_color = DEFAULT_FONT_COLOR

    if isinstance(element, Checkbox):
        new_element.value = CHECKBOX_TO_DRAW
    elif isinstance(element, Radio):
        new_element.value = RADIO_TO_DRAW

    return new_element


def preview_element_to_draw(element: ELEMENT_TYPES) -> Text:
    """Converts an element to a preview text element."""

    new_element = Text(
        element_name=element.name,
        element_value="{" + f" {element.name} " + "}",
    )
    new_element.font = DEFAULT_FONT
    new_element.font_size = DEFAULT_FONT_SIZE
    new_element.font_color = PREVIEW_FONT_COLOR
    new_element.preview = True

    return new_element


def remove_all_elements(pdf: bytes) -> bytes:
    """Removes all elements from a pdfrw parsed PDF form."""

    pdf = PdfReader(fdata=pdf)

    for page in pdf.pages:
        elements = page[ANNOTATION_KEY]
        if elements:
            for j in reversed(range(len(elements))):
                elements.pop(j)

    return generate_stream(pdf)


def get_page_streams(pdf: bytes) -> List[bytes]:
    """Returns a list of streams where each is a page of the input PDF."""

    pdf = PdfReader(fdata=pdf)
    result = []

    for page in pdf.pages:
        writer = PdfWriter()
        writer.addPage(page)
        with BytesIO() as f:
            writer.write(f)
            f.seek(0)
            result.append(f.read())

    return result


def merge_two_pdfs(pdf: bytes, other: bytes) -> bytes:
    """Merges two PDFs into one PDF."""

    writer = PdfWriter()

    writer.addpages(PdfReader(fdata=pdf).pages)
    writer.addpages(PdfReader(fdata=other).pages)

    result_stream = BytesIO()
    writer.write(result_stream)
    result_stream.seek(0)

    result = result_stream.read()
    result_stream.close()

    return result


def find_pattern_match(pattern: dict, element: PdfDict) -> bool:
    """Checks if a PDF dict pattern exists in a PDF element."""

    for key, value in element.items():
        result = False
        if key in pattern:
            if isinstance(pattern[key], dict) and isinstance(value, PdfDict):
                result = find_pattern_match(pattern[key], value)
            else:
                result = pattern[key] == value
        if result:
            return result
    return False


def traverse_pattern(pattern: dict, element: PdfDict) -> Union[str, list, None]:
    """Traverses down a PDF dict pattern and find the value."""

    for key, value in element.items():
        result = None
        if key in pattern:
            if isinstance(pattern[key], dict) and isinstance(value, PdfDict):
                result = traverse_pattern(pattern[key], value)
            else:
                if pattern[key] is True and value:
                    return value
        if result:
            return result
    return None
