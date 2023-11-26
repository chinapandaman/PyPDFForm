# -*- coding: utf-8 -*-
"""Contains helpers for font."""

from io import BytesIO
from math import sqrt
from re import findall
from typing import Dict, Tuple, Union

from pdfrw import PdfDict, PdfReader
from reportlab.pdfbase.pdfmetrics import registerFont, standardFonts
from reportlab.pdfbase.ttfonts import TTFError, TTFont

from ..middleware.constants import ELEMENT_TYPES
from ..middleware.text import Text
from .constants import (ANNOTATION_RECTANGLE_KEY, DEFAULT_FONT,
                        DEFAULT_FONT_SIZE, FONT_COLOR_IDENTIFIER,
                        FONT_SIZE_IDENTIFIER)
from .patterns import TEXT_FIELD_APPEARANCE_PATTERNS
from .template import (get_element_key, get_elements_by_page,
                       get_paragraph_auto_wrap_length, get_paragraph_lines,
                       is_text_multiline)
from .utils import traverse_pattern


def register_font(font_name: str, ttf_stream: bytes) -> bool:
    """Registers a font from a ttf file stream."""

    buff = BytesIO()
    buff.write(ttf_stream)
    buff.seek(0)

    try:
        registerFont(TTFont(name=font_name, filename=buff))
        result = True
    except TTFError:
        result = False

    buff.close()
    return result


def auto_detect_font(element: PdfDict) -> str:
    """Returns the font of the text field if it is one of the standard fonts."""

    result = DEFAULT_FONT

    text_appearance = None
    for pattern in TEXT_FIELD_APPEARANCE_PATTERNS:
        text_appearance = traverse_pattern(pattern, element)

        if text_appearance:
            break

    if not text_appearance:
        return result

    text_appearance = text_appearance.replace("(", "").replace(")", "").split(" ")

    for each in text_appearance:
        if each.startswith("/"):
            text_segments = findall("[A-Z][^A-Z]*", each.replace("/", ""))

            for font in standardFonts:
                font_segments = findall("[A-Z][^A-Z]*", font.replace("-", ""))
                if len(font_segments) != len(text_segments):
                    continue

                found = True
                for i, val in enumerate(font_segments):
                    if not val.startswith(text_segments[i]):
                        found = False

                if found:
                    return font

    return result


def text_field_font_size(element: PdfDict) -> Union[float, int]:
    """
    Calculates the font size it should be drawn with
    given a text field element.
    """

    if is_text_multiline(element):
        return DEFAULT_FONT_SIZE

    height = abs(
        float(element[ANNOTATION_RECTANGLE_KEY][1])
        - float(element[ANNOTATION_RECTANGLE_KEY][3])
    )

    return height * 2 / 3


def checkbox_radio_font_size(element: PdfDict) -> Union[float, int]:
    """
    Calculates the font size it should be drawn with
    given a checkbox/radio button element.
    """

    area = abs(
        float(element[ANNOTATION_RECTANGLE_KEY][0])
        - float(element[ANNOTATION_RECTANGLE_KEY][2])
    ) * abs(
        float(element[ANNOTATION_RECTANGLE_KEY][1])
        - float(element[ANNOTATION_RECTANGLE_KEY][3])
    )

    return sqrt(area) * 72 / 96


def get_text_field_font_size(element: PdfDict) -> Union[float, int]:
    """Returns the font size of the text field if presented or zero."""

    result = 0
    for pattern in TEXT_FIELD_APPEARANCE_PATTERNS:
        text_appearance = traverse_pattern(pattern, element)
        if text_appearance:
            text_appearance = text_appearance.replace("(", "").replace(")", "")
            properties = text_appearance.split(" ")
            for i, val in enumerate(properties):
                if val == FONT_SIZE_IDENTIFIER:
                    return float(properties[i - 1])

    return result


def get_text_field_font_color(
    element: PdfDict,
) -> Union[Tuple[float, float, float], None]:
    """Returns the font color tuple of the text field if presented or black."""

    result = (0, 0, 0)
    for pattern in TEXT_FIELD_APPEARANCE_PATTERNS:
        text_appearance = traverse_pattern(pattern, element)
        if text_appearance:
            if FONT_COLOR_IDENTIFIER not in text_appearance:
                return result

            text_appearance = (
                text_appearance.replace("(", "").replace(")", "").split(" ")
            )
            for i, val in enumerate(text_appearance):
                if val == FONT_COLOR_IDENTIFIER.replace(" ", ""):
                    result = (
                        float(text_appearance[i - 3]),
                        float(text_appearance[i - 2]),
                        float(text_appearance[i - 1]),
                    )
                    break

    return result


def update_text_field_attributes(
    template_stream: bytes,
    elements: Dict[str, ELEMENT_TYPES],
) -> None:
    """Auto updates text fields' attributes."""

    template_pdf = PdfReader(fdata=template_stream)

    for _, _elements in get_elements_by_page(template_pdf).items():
        for _element in _elements:
            key = get_element_key(_element)

            if isinstance(elements[key], Text):
                if elements[key].font is None:
                    elements[key].font = auto_detect_font(_element)
                if elements[key].font_size is None:
                    elements[key].font_size = get_text_field_font_size(
                        _element
                    ) or text_field_font_size(_element)
                if elements[key].font_color is None:
                    elements[key].font_color = get_text_field_font_color(_element)
                if (
                    is_text_multiline(_element)
                    and elements[key].text_wrap_length is None
                ):
                    elements[key].text_wrap_length = get_paragraph_auto_wrap_length(
                        _element, elements[key]
                    )
                    elements[key].text_lines = get_paragraph_lines(elements[key])
