# -*- coding: utf-8 -*-
"""Contains helpers for font."""

from io import BytesIO
from math import sqrt
from re import findall
from typing import Tuple, Union

from reportlab.pdfbase.acroform import AcroForm
from reportlab.pdfbase.pdfmetrics import (registerFont, standardFonts,
                                          stringWidth)
from reportlab.pdfbase.ttfonts import TTFError, TTFont

from .constants import (DEFAULT_FONT, FONT_COLOR_IDENTIFIER,
                        FONT_SIZE_IDENTIFIER, FONT_SIZE_REDUCE_STEP,
                        MARGIN_BETWEEN_LINES, Rect)
from .middleware.text import Text
from .patterns import TEXT_FIELD_APPEARANCE_PATTERNS
from .utils import extract_widget_property


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


def extract_font_from_text_appearance(text_appearance: str) -> Union[str, None]:
    """
    Uses regex to pattern match out the font from the text
    appearance string of a text field widget.
    """

    text_appearances = text_appearance.split(" ")

    for each in text_appearances:
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

    return None


def auto_detect_font(widget: dict) -> str:
    """Returns the font of the text field if it is one of the standard fonts."""

    text_appearance = extract_widget_property(
        widget, TEXT_FIELD_APPEARANCE_PATTERNS, None, None
    )

    if not text_appearance:
        return DEFAULT_FONT

    return extract_font_from_text_appearance(text_appearance) or DEFAULT_FONT


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
    text_appearance = extract_widget_property(
        widget, TEXT_FIELD_APPEARANCE_PATTERNS, None, None
    )
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
    text_appearance = extract_widget_property(
        widget, TEXT_FIELD_APPEARANCE_PATTERNS, None, None
    )
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


def adjust_paragraph_font_size(widget: dict, widget_middleware: Text) -> None:
    """Reduces the font size of a paragraph field until texts fits."""

    # pylint: disable=C0415, R0401
    from .template import get_paragraph_lines

    height = abs(float(widget[Rect][1]) - float(widget[Rect][3]))

    while (
        widget_middleware.font_size > FONT_SIZE_REDUCE_STEP
        and len(widget_middleware.text_lines)
        * (widget_middleware.font_size + MARGIN_BETWEEN_LINES)
        > height
    ):
        widget_middleware.font_size -= FONT_SIZE_REDUCE_STEP
        widget_middleware.text_lines = get_paragraph_lines(widget, widget_middleware)


def adjust_text_field_font_size(widget: dict, widget_middleware: Text) -> None:
    """Reduces the font size of a text field until texts fits."""

    width = abs(float(widget[Rect][0]) - float(widget[Rect][2]))

    while (
        widget_middleware.font_size > FONT_SIZE_REDUCE_STEP
        and stringWidth(
            widget_middleware.value, widget_middleware.font, widget_middleware.font_size
        )
        > width
    ):
        widget_middleware.font_size -= FONT_SIZE_REDUCE_STEP
