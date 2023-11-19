# -*- coding: utf-8 -*-
"""Contains utility helpers."""

from io import BytesIO
from typing import Union

import pdfrw

from ..middleware.checkbox import Checkbox
from ..middleware.constants import ELEMENT_TYPES
from ..middleware.radio import Radio
from ..middleware.text import Text
from . import constants


def generate_stream(pdf: pdfrw.PdfReader) -> bytes:
    """Generates new stream for manipulated PDF form."""

    result_stream = BytesIO()

    pdfrw.PdfWriter().write(result_stream, pdf)
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
    new_element.font = constants.DEFAULT_FONT
    new_element.font_size = font_size
    new_element.font_color = constants.DEFAULT_FONT_COLOR

    if isinstance(element, Checkbox):
        new_element.value = constants.CHECKBOX_TO_DRAW
    elif isinstance(element, Radio):
        new_element.value = constants.RADIO_TO_DRAW

    return new_element


def preview_element_to_draw(element: ELEMENT_TYPES) -> Text:
    """Converts an element to a preview text element."""

    new_element = Text(
        element_name=element.name,
        element_value="{" + f" {element.name} " + "}",
    )
    new_element.font = constants.DEFAULT_FONT
    new_element.font_size = constants.DEFAULT_FONT_SIZE
    new_element.font_color = constants.PREVIEW_FONT_COLOR
    new_element.preview = True

    return new_element


def remove_all_elements(pdf: bytes) -> bytes:
    """Removes all elements from a pdfrw parsed PDF form."""

    pdf = pdfrw.PdfReader(fdata=pdf)

    for page in pdf.pages:
        elements = page[constants.ANNOTATION_KEY]
        if elements:
            for j in reversed(range(len(elements))):
                elements.pop(j)

    return generate_stream(pdf)


def merge_two_pdfs(pdf: bytes, other: bytes) -> bytes:
    """Merges two PDFs into one PDF."""

    writer = pdfrw.PdfWriter()

    writer.addpages(pdfrw.PdfReader(fdata=pdf).pages)
    writer.addpages(pdfrw.PdfReader(fdata=other).pages)

    result_stream = BytesIO()
    writer.write(result_stream)
    result_stream.seek(0)

    result = result_stream.read()
    result_stream.close()

    return result


def find_pattern_match(pattern: dict, element: pdfrw.PdfDict) -> bool:
    """Checks if a PDF dict pattern exists in a PDF element."""

    for key, value in element.items():
        result = False
        if key in pattern:
            if isinstance(pattern[key], dict) and isinstance(value, pdfrw.PdfDict):
                result = find_pattern_match(pattern[key], value)
            else:
                result = pattern[key] == value
        if result:
            return result
    return False


def traverse_pattern(pattern: dict, element: pdfrw.PdfDict) -> Union[str, list, None]:
    """Traverses down a PDF dict pattern and find the value."""

    for key, value in element.items():
        result = None
        if key in pattern:
            if isinstance(pattern[key], dict) and isinstance(value, pdfrw.PdfDict):
                result = traverse_pattern(pattern[key], value)
            else:
                if pattern[key] is True and value:
                    return value
        if result:
            return result
    return None
