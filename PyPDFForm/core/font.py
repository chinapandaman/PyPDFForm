# -*- coding: utf-8 -*-
"""Contains helpers for font."""

import pdfrw
from io import BytesIO

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
                    for font in pdfmetrics.standardFonts:
                        if font.startswith(each.replace("/", "")):
                            return font

    return result
