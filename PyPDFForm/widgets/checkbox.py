# -*- coding: utf-8 -*-

from .base import Widget


class CheckBoxWidget(Widget):
    USER_PARAMS = [
        ("button_style", "buttonStyle"),
        ("tick_color", "textColor"),
        ("bg_color", "fillColor"),
        ("border_color", "borderColor"),
        ("border_width", "borderWidth"),
    ]
    COLOR_PARAMS = ["tick_color", "bg_color", "border_color"]
    ALLOWED_HOOK_PARAMS = ["size"]
    ACRO_FORM_FUNC = "checkbox"
