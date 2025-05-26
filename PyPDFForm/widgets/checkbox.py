# -*- coding: utf-8 -*-
"""
This module defines the CheckBoxWidget class, which is a subclass of the
Widget class. It represents a checkbox form field in a PDF document.
"""

from .base import Widget


class CheckBoxWidget(Widget):
    """
    Represents a checkbox widget in a PDF form.

    Inherits from the base Widget class and adds specific parameters for
    checkbox styling, such as button style, tick color, background color,
    border color, and border width.

    Attributes:
        USER_PARAMS (list): A list of tuples, where each tuple contains the
            user-facing parameter name and the corresponding AcroForm parameter name.
        COLOR_PARAMS (list): A list of user-facing parameter names that represent colors.
        ALLOWED_HOOK_PARAMS (list): A list of allowed hook parameters.
        ACRO_FORM_FUNC (str): The name of the AcroForm function to use for
            creating the checkbox.
    """

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
