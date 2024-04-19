# -*- coding: utf-8 -*-
"""Contains checkbox widget to create."""

from .base import Widget


class CheckBoxWidget(Widget):
    """Checkbox widget to create."""

    USER_PARAMS = [
        ("size", "size"),
        ("button_style", "buttonStyle"),
        ("tick_color", "textColor"),
        ("bg_color", "fillColor"),
        ("border_color", "borderColor"),
        ("border_width", "borderWidth"),
    ]
    COLOR_PARAMS = ["tick_color", "bg_color", "border_color"]
    ACRO_FORM_FUNC = "checkbox"
