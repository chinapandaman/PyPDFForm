# -*- coding: utf-8 -*-
"""
This module defines the `CheckBoxField` and `CheckBoxWidget` classes, which are
used to represent and manipulate checkbox form fields within PDF documents.

The `CheckBoxField` class is a dataclass that encapsulates the properties of a
checkbox field, such as its size, style, and colors.

The `CheckBoxWidget` class extends the base `Widget` class to provide specific
functionality for interacting with checkbox form fields in PDFs.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Type

from .base import Field, Widget


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
        ("required", "required"),
        ("tooltip", "tooltip"),
        ("button_style", "buttonStyle"),
        ("tick_color", "textColor"),
        ("bg_color", "fillColor"),
        ("border_color", "borderColor"),
        ("border_width", "borderWidth"),
    ]
    COLOR_PARAMS = ["tick_color", "bg_color", "border_color"]
    ALLOWED_HOOK_PARAMS = ["size"]
    ACRO_FORM_FUNC = "checkbox"


@dataclass
class CheckBoxField(Field):
    """
    Represents a checkbox field in a PDF document.

    This dataclass extends the `Field` base class and defines the specific
    attributes that can be configured for a checkbox field.

    Attributes:
        _field_type (str): The type of the field, fixed as "checkbox".
        _widget_class (Type[Widget]): The widget class associated with this field type.
        size (Optional[float]): The size of the checkbox.
        button_style (Optional[str]): The visual style of the checkbox button
            (e.g., "check", "circle", "cross").
        tick_color (Optional[Tuple[float, ...]]): The color of the checkmark or tick.
        bg_color (Optional[Tuple[float, ...]]): The background color of the checkbox.
        border_color (Optional[Tuple[float, ...]]): The color of the checkbox's border.
        border_width (Optional[float]): The width of the checkbox's border.
    """

    _field_type: str = "checkbox"
    _widget_class: Type[Widget] = CheckBoxWidget

    size: Optional[float] = None
    button_style: Optional[str] = None
    tick_color: Optional[Tuple[float, ...]] = None
    bg_color: Optional[Tuple[float, ...]] = None
    border_color: Optional[Tuple[float, ...]] = None
    border_width: Optional[float] = None
