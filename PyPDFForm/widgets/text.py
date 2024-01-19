# -*- coding: utf-8 -*-
"""Contains text field widget to create."""

from .base import Widget


class TextWidget(Widget):
    """Text field widget to create."""

    USER_PARAMS = [
        ("width", "width"),
        ("height", "height"),
        ("max_length", "maxlen"),
        ("font", "fontName"),
        ("font_size", "fontSize"),
        ("font_color", "textColor"),
    ]
    COLOR_PARAMS = ["font_color"]
    NONE_DEFAULTS = ["max_length"]
    ACRO_FORM_FUNC = "textfield"
