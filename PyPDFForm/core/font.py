# -*- coding: utf-8 -*-
"""Contains helpers for font."""

import pdfrw
from io import BytesIO
import re

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError, TTFont
from .patterns import TEXT_FIELD_APPEARANCE_PATTERNS
from .template import traverse_pattern
from . import constants


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

        if text_appearance:
            text_appearance = (
                text_appearance.replace("(", "").replace(")", "").split(" ")
            )

            for each in text_appearance:
                if each.startswith("/"):
                    text_segments = re.findall('[A-Z][^A-Z]*', each.replace("/", ""))

                    for font in pdfmetrics.standardFonts:
                        font_segments = re.findall('[A-Z][^A-Z]*', font.replace("-", ""))
                        if len(font_segments) != len(text_segments):
                            continue

                        found = True
                        for i, val in enumerate(font_segments):
                            if not val.startswith(text_segments[i]):
                                found = False

                        if found:
                            return font

    return result
