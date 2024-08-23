# -*- coding: utf-8 -*-
"""Contains text field widget to create."""

from .base import Widget


class TextWidget(Widget):
    """Text field widget to create."""

    USER_PARAMS = [
        ("width", "width"),
        ("height", "height"),
        ("font", "fontName"),
        ("font_size", "fontSize"),
        ("font_color", "textColor"),
        ("bg_color", "fillColor"),
        ("border_color", "borderColor"),
        ("border_width", "borderWidth"),
        ("max_length", "maxlen"),
    ]
    COLOR_PARAMS = ["font_color", "bg_color", "border_color"]
    ALLOWED_NON_ACRO_FORM_PARAMS = ["alignment", "multiline"]
    NONE_DEFAULTS = ["max_length"]
    ACRO_FORM_FUNC = "textfield"
