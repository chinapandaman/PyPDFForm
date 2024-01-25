# -*- coding: utf-8 -*-
"""Contains checkbox widget to create."""

from .base import Widget


class CheckBoxWidget(Widget):
    """Checkbox widget to create."""

    USER_PARAMS = [("size", "size"), ("button_style", "buttonStyle")]
    ACRO_FORM_FUNC = "checkbox"
