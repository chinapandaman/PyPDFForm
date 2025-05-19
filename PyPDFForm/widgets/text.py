# -*- coding: utf-8 -*-
"""Provides text field widget creation functionality for PDF forms.

This module contains the TextWidget class which handles creation of:
- Standard text input fields
- Multiline text fields
- Font and color styling
- Field size and length constraints
"""

from .base import Widget


class TextWidget(Widget):
    """Creates and configures PDF text field widgets.

    Supports all standard text field properties including:
    - Font styling (family, size, color)
    - Background and border colors
    - Width/height dimensions
    - Maximum length constraints
    - Alignment and multiline options

    Inherits from Widget base class adding text-specific parameters.
    """

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
    ALLOWED_NON_ACRO_FORM_PARAMS = ["alignment", "multiline", "comb"]
    NONE_DEFAULTS = ["max_length"]
    ACRO_FORM_FUNC = "textfield"
