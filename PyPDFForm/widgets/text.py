# -*- coding: utf-8 -*-
"""
This module defines the TextWidget class, which is a subclass of the
Widget class. It represents a text field in a PDF document.
"""

from .base import Widget


class TextWidget(Widget):
    """
    Represents a text widget in a PDF form.

    This class inherits from the base Widget class and provides specific
    parameters for text field styling, such as width, height, font size,
    font color, background color, border color, border width, and maximum
    length.

    Attributes:
        USER_PARAMS (list): A list of tuples, where each tuple contains the
            user-facing parameter name and the corresponding AcroForm parameter name.
        COLOR_PARAMS (list): A list of user-facing parameter names that represent colors.
        ALLOWED_HOOK_PARAMS (list): A list of allowed hook parameters.
        NONE_DEFAULTS (list): A list of parameters that default to None.
        ACRO_FORM_FUNC (str): The name of the AcroForm function to use for
            creating the text field.
    """

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
    ALLOWED_HOOK_PARAMS = ["required", "alignment", "multiline", "comb", "font"]
    NONE_DEFAULTS = ["max_length"]
    ACRO_FORM_FUNC = "textfield"
