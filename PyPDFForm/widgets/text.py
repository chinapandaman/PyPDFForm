# -*- coding: utf-8 -*-
"""Contains text field widget to create."""

from .base import Widget


class TextWidget(Widget):
    """Text field widget to create."""

    USER_PARAMS = ["width", "height", "maxlen"]
    NONE_DEFAULTS = ["maxlen"]
    ACRO_FORM_FUNC = "textfield"
