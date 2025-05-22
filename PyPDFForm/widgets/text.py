# -*- coding: utf-8 -*-

from .base import Widget


class TextWidget(Widget):
    USER_PARAMS = [
        ("width", "width"),
        ("height", "height"),
        ("font_size", "fontSize"),
        ("font_color", "textColor"),
        ("bg_color", "fillColor"),
        ("border_color", "borderColor"),
        ("border_width", "borderWidth"),
        ("max_length", "maxlen"),
    ]
    COLOR_PARAMS = ["font_color", "bg_color", "border_color"]
    ALLOWED_HOOK_PARAMS = ["alignment", "multiline", "comb", "font"]
    NONE_DEFAULTS = ["max_length"]
    ACRO_FORM_FUNC = "textfield"
