# -*- coding: utf-8 -*-
"""Contains helpers for font."""

from io import BytesIO

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError, TTFont


class Font:
    """Contains methods for interacting with fonts."""

    @staticmethod
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

    @staticmethod
    def is_registered(font_name: str) -> bool:
        """Checks if a font is registered."""

        try:
            pdfmetrics.getFont(font_name)
            return True
        except KeyError:
            return False
