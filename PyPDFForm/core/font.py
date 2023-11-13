# -*- coding: utf-8 -*-
"""Contains helpers for font."""

import re
from io import BytesIO
from typing import Union
from math import sqrt

import pdfrw
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError, TTFont

from . import constants
from .patterns import TEXT_FIELD_APPEARANCE_PATTERNS
from .template import traverse_pattern, is_text_multiline
from .constants import DEFAULT_FONT_SIZE


def register_font(font_name: str, ttf_stream: bytes) -> bool:
    """Registers a font from a ttf file stream."""

    buff = BytesIO()
    buff.write(ttf_stream)
    buff.seek(0)

    try:
        pdfmetrics.registerFont(TTFont(name=font_name, filename=buff))
        result = True
    except TTFError:
        result = False

    buff.close()
    return result


def auto_detect_font(element: pdfrw.PdfDict) -> str:
    """Returns the font of the text field if it is one of the standard fonts."""

    result = constants.DEFAULT_FONT

    for pattern in TEXT_FIELD_APPEARANCE_PATTERNS:
        text_appearance = traverse_pattern(pattern, element)

        if not text_appearance:
            return result

        text_appearance = text_appearance.replace("(", "").replace(")", "").split(" ")

        for each in text_appearance:
            if not each.startswith("/"):
                return result

            text_segments = re.findall("[A-Z][^A-Z]*", each.replace("/", ""))

            for font in pdfmetrics.standardFonts:
                font_segments = re.findall("[A-Z][^A-Z]*", font.replace("-", ""))
                if len(font_segments) != len(text_segments):
                    continue

                found = True
                for i, val in enumerate(font_segments):
                    if not val.startswith(text_segments[i]):
                        found = False

                if found:
                    return font

    return result


def text_field_font_size(element: pdfrw.PdfDict) -> Union[float, int]:
    """
    Calculates the font size it should be drawn with
    given a text field element.
    """

    if is_text_multiline(element):
        return DEFAULT_FONT_SIZE

    height = abs(
        float(element[constants.ANNOTATION_RECTANGLE_KEY][1])
        - float(element[constants.ANNOTATION_RECTANGLE_KEY][3])
    )

    return height * 2 / 3


def checkbox_radio_font_size(element: pdfrw.PdfDict) -> Union[float, int]:
    """
    Calculates the font size it should be drawn with
    given a checkbox/radio button element.
    """

    area = abs(
        float(element[constants.ANNOTATION_RECTANGLE_KEY][0])
        - float(element[constants.ANNOTATION_RECTANGLE_KEY][2])
    ) * abs(
        float(element[constants.ANNOTATION_RECTANGLE_KEY][1])
        - float(element[constants.ANNOTATION_RECTANGLE_KEY][3])
    )

    return sqrt(area) * 72 / 96
