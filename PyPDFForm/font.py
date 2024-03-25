# -*- coding: utf-8 -*-
"""Contains helpers for font."""

from io import BytesIO
from math import sqrt
from re import findall
from typing import Tuple, Union

from reportlab.pdfbase.acroform import AcroForm
from reportlab.pdfbase.pdfmetrics import registerFont, standardFonts
from reportlab.pdfbase.ttfonts import TTFError, TTFont

from .constants import (DEFAULT_FONT, FONT_COLOR_IDENTIFIER,
                        FONT_SIZE_IDENTIFIER, Rect)
from .patterns import TEXT_FIELD_APPEARANCE_PATTERNS
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


def auto_detect_font(widget: dict) -> str:
    """Returns the font of the text field if it is one of the standard fonts."""

    # pylint: disable=R0912
    result = DEFAULT_FONT

    text_appearance = None
    for pattern in TEXT_FIELD_APPEARANCE_PATTERNS:
        text_appearance = traverse_pattern(pattern, widget)

        if text_appearance:
            break

    if not text_appearance:
        return result

    text_appearance = text_appearance.split(" ")

    for each in text_appearance:
        if each.startswith("/"):
            text_segments = findall("[A-Z][^A-Z]*", each.replace("/", ""))

            if len(text_segments) == 1:
                for k, v in AcroForm.formFontNames.items():
                    if v == text_segments[0]:
                        return k

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


def text_field_font_size(widget: dict) -> Union[float, int]:
    """
    Calculates the font size it should be drawn with
    given a text field widget.
    """

    height = abs(float(widget[Rect][1]) - float(widget[Rect][3]))

    return height * 2 / 3


def checkbox_radio_font_size(widget: dict) -> Union[float, int]:
    """
    Calculates the font size it should be drawn with
    given a checkbox/radio button widget.
    """

    area = abs(float(widget[Rect][0]) - float(widget[Rect][2])) * abs(
        float(widget[Rect][1]) - float(widget[Rect][3])
    )

    return sqrt(area) * 72 / 96


def get_text_field_font_size(widget: dict) -> Union[float, int]:
    """Returns the font size of the text field if presented or zero."""

    result = 0
    for pattern in TEXT_FIELD_APPEARANCE_PATTERNS:
        text_appearance = traverse_pattern(pattern, widget)
        if text_appearance:
            properties = text_appearance.split(" ")
            for i, val in enumerate(properties):
                if val.startswith(FONT_SIZE_IDENTIFIER):
                    return float(properties[i - 1])

    return result


def get_text_field_font_color(
    widget: dict,
) -> Union[Tuple[float, float, float], None]:
    """Returns the font color tuple of the text field if presented or black."""

    result = (0, 0, 0)
    for pattern in TEXT_FIELD_APPEARANCE_PATTERNS:
        text_appearance = traverse_pattern(pattern, widget)
        if text_appearance:
            if FONT_COLOR_IDENTIFIER not in text_appearance:
                return result

            text_appearance = text_appearance.split(" ")
            for i, val in enumerate(text_appearance):
                if val.startswith(FONT_COLOR_IDENTIFIER.replace(" ", "")):
                    result = (
                        float(text_appearance[i - 3]),
                        float(text_appearance[i - 2]),
                        float(text_appearance[i - 1]),
                    )
                    break

    return result
